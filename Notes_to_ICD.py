#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 9 12:18:26 2023

@author: John Ciubuc
"""
import streamlit as st
st.set_page_config(
    page_title="Notes to ICD by John Ciubuc",
    initial_sidebar_state="collapsed"
      # layout="wide"
  )

from streamlit import session_state as _st
from modules import notes_to_icd as core
from modules import snomed
from helpers import st_functions as stf
from annotated_text import util as at_util
import numpy as np
import pickle
import bisect

complex_thresholds = [0,0.6,0.85]
complex_list = ['Low',
               'Medium',
               'High']

complexity_wrap = [lambda x : f' :orange[{x}]',
                   lambda x : f':blue[{x}]',
                   lambda x : f':green[{x}]']

st_write_type_wrap = [lambda a, x : a.error(x), 
              lambda a, x : a.warning(x), 
              lambda a, x : a.info(x)]

complex_code_list = [99203,
                     99204,
                     99205,
                     99213,
                     99214,
                     99215]

long_visit = [(60, 99205),
              (40, 99215)]


def generate_code_improvements(scores, score_texts, codes):
    score_z = zip(scores, score_texts, codes)
    score_z = sorted(score_z, key=lambda x: x[0])
    score_z = [x for x in score_z if x[0] != -1 and x[0] < 0.6]
    if len(score_z) == 0:
        st.markdown('This section was :blue[Exceptional]. We can not recommend any additional :green[code improvements] based on the note content submitted')
        return
    st.markdown('Code complexity can be increased by being more specific. Room for improvement include:')
    for entity in score_z:
        reconst_list = [f'Instead of {entity[1]}, consider ']
        reconst_list = list(stf.reconstitute_paragraph_gen(reconst_list, entity[1], entity[0]))
        try:
            sno_ent = snomed.SNOMEDCT[entity[2]]
            sno_desc = list(sno_ent.descendants_no_double())
            if len(sno_desc) > 3:
                sno_len = 3
            else:
                sno_len = len(sno_desc)
            print('after 3')
            for i in range(0,sno_len):
                print(f'trying')
                print(f'try:{sno_desc[i].term}')
                reconst_list.append((sno_desc[i].term, '', '#800080'))
                reconst_list.append(' and ')
            reconst_list = reconst_list[:-1]
            reconst_list.append('\n\n')
            st.markdown(
                at_util.get_annotated_html(*reconst_list),
                unsafe_allow_html=True,
            )
            st.write('')
        except:
            print('whoops')
       
            

def generate_office_visit(all_avg_scores):
    avg_score = np.average(all_avg_scores)
    # get note complexity
    c_level = bisect.bisect(complex_thresholds, avg_score) - 1
    # Generate suggestions
    complexity = complexity_wrap[c_level](complex_list[c_level])
    st_write_type_wrap[c_level](st, f'The average complexity of this note is {complexity} (Score: {avg_score:.2f})')
    st_write_type_wrap[c_level](st, f"""Recommend billing {complexity_wrap[c_level](complex_code_list[c_level])} 
                        if this is a new patient, or billing {complexity_wrap[c_level](complex_code_list[c_level+3])} 
                        if this is an existing patient visit
                        """)
                        
def generate_office_time_recommendation(rec_type):
    match rec_type:
        case 'HPI':
            st_write_type_wrap[2](st, f"""The HPI section has a considerable amount of information in it. 
                                  If you spent more than {long_visit[0][0]} minutes on a new patient, consider billing {complexity_wrap[2](long_visit[0][1])}.
                                  If this is an established patient and you spent more than {long_visit[1][0]} minutes, consider billing {complexity_wrap[2](long_visit[1][1])}""")
        case 'AP':
            st_write_type_wrap[2](st, f"""The Assessment and Plan section has a considerable amount of complexity in it. 
                                  Consider billing {complexity_wrap[2](long_visit[0][1])} for a new patient, or {complexity_wrap[2](long_visit[1][1])} for an established patient.""")
    
def run():
    # Session variables 
    if 'note_run' not in _st:
        _st.note_run = False
    
    if 'note_data' not in _st:
        _st.note_data = ''
    
    if not st.session_state.note_run:
        text_input = st.empty()
        _st.note_data = text_input.text_area('Enter a clinical note to :blue[Analyze]. Note needs to be in the :orange[**AllScripts**] format', '', height=400)
        #, label_visibility=st.session_state.textarea_vis
        
    
        # center_col = col1.columns((1, 2, 1))
        # a = center_col[1].button('Analyze Student Note')
        analyze_button = st.empty()
        a = analyze_button.button('Analyze Note')
    else:
        a = True
    
    if a:
        # Hide first page
        try:
            text_input.empty()
            analyze_button.empty()
        except:
            print('Button Empty')
    
        note, note_sections = core.set_sections_on_clips(_st.note_data, False)
        note, note_section_indexes = core.recombine_for_aws(note_sections)
        with st.spinner('Running NLP...'):
            entities = core.request_amazon(note);
        # file = open('aws_response.pkl', 'rb')
        # entities = pickle.load(file)
        # file.close()
        
        debType = 'ENT'
        entities_low, entities_high = core.prune_entities_to_confidence(entities[debType])
        entity_sections = core.reformat_entities_to_section(entities_high,note_section_indexes)
    
        # note_sections[0]
        # entity_sections
        # Create streamlit page
        
        # ICD Codes
        tab_container = st.empty()
        Tabs = tab_container.tabs(["💻 Reason For Visit", 
                              "🗃 Review of Systems", 
                              "🧭 Physical Exam", 
                              "🗺️ Assessment and  Plan"])
        
        tab_list = ['Reason For Visit', 'Review of Systems', 'Physical Exam', 'Assessment']
        all_avg_scores = []
        scores_sections = []
        score_texts_sections = []
        codes_sections = []

        for i in range(0,len(Tabs)):
            with Tabs[i]:
                entity_list = []
                col2_write_list = []
                for ents in entity_sections[tab_list[i]]:  
                    col2_write_list.append(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
                    entity_list.append({ents['Text']: ents['ICD10CMConcepts']})
                    
                para, scores, score_texts, codes = stf.generate_annotated_paragraph(note_sections[i], entity_list)
                avg_score = np.average([x for x in scores if x != -1])
                
                # saving for out of loop
                all_avg_scores.append(avg_score)
                scores_sections.append(scores)
                score_texts_sections.append(score_texts)
                codes_sections.append(codes)
                
                # Complexity string for user
                c_level = bisect.bisect(complex_thresholds, avg_score) - 1 
                complexity = complexity_wrap[c_level](complex_list[c_level])
                    
                st.info(f"Complexity for this section is: {complexity} (Score: {avg_score:0.2f})")
                col1, col2 = st.columns(2)
                col1.markdown("### Note Section")
                # col1.markdown("-----")
                col2.markdown("### ICD-10 Codes")
                # col2.markdown("-----")
                # Generate paragraph for this section
                # para = note_sections[i]
                # with col1:
                # st.write(para)
                for i,w in enumerate(col2_write_list):
                    c_level = bisect.bisect(complex_thresholds, scores[i]) - 1 
                    st_write_type_wrap[c_level](col2, w)
                    
                # Write annotated html    
                col1.markdown(
                    at_util.get_annotated_html(*para),
                    unsafe_allow_html=True,
                )
            
        st.markdown('-----')
        generate_office_visit(all_avg_scores)
        # Arbitrary number for a large HPI
        if len(note_sections[0]) > 800:
            generate_office_time_recommendation('HPI')
        # Complicated AP
        if all_avg_scores[3] > complex_thresholds[2]:
            generate_office_time_recommendation('AP')
        st.markdown('-----')
        st.markdown('### Recommended Code Improvements:')
        Tabs = st.tabs(["💻 Reason For Visit", 
                              "🗃 Review of Systems", 
                              "🧭 Physical Exam", 
                              "🗺️ Assessment and  Plan"])
        for i in range(0,len(Tabs)):
            with Tabs[i]:
                generate_code_improvements(scores_sections[i], 
                                           score_texts_sections[i],
                                           codes_sections[i])
        
            
    
if __name__ == "__main__":
    run()