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
from helpers import st_functions as stf
from annotated_text import annotated_text
import pickle

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
        # entities = core.request_amazon(note);
        file = open('aws_response.pkl', 'rb')
        entities = pickle.load(file)
        file.close()
        
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
        for i in range(0,len(Tabs)):
            with Tabs[i]:
                col1, col2 = st.columns(2)
                entity_list = []
                for ents in entity_sections[tab_list[i]]:  
                    col2.write(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
                    # Save user terms and icd descriptions for tagging
                    entity_list.append({ents['Text']: ents['ICD10CMConcepts'][0]['Description']})
                    
                para = stf.generate_annotated_paragraph(note_sections[i], entity_list)
                # Generate paragraph for this section
                # para = note_sections[i]
                # with col1:
                # st.write(para)
                annotated_text(*para)

                
             
     
    
    
    
    
    
    
    
if __name__ == "__main__":
    run()