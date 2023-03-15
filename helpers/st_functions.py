#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 16:41:42 2023

@author: John Ciubuc
"""

import streamlit as st
import re
import numpy as np
import pandas as pd
from itertools import compress

def generate_number_point_rubric(index, value=0):
    num_inp = st.number_input("Maximum Points in this Sections", 
                             value = value,
                             step = 1,
                             format = '%d',
                             help = "Maximum number of points a student can get in this section.",
                             key=f'number_input_{index}')
    return num_inp


def generate_tab_section_rubric(index, config, saver):
    Entities = {}
    Entities[config.SECTIONS[index]] = []
    
    config_section = config.SECTIONS[index]

    # Entities[config.SECTIONS[index]] ['Points'] = points
    
    # columns = st.columns([3,1])
    # st.write(Entities[config.SECTIONS[index]])
    st.write('##### Uncheck an item below to remove it from the Rubric')
    for i,entity in enumerate(saver['Entity High'][config_section]):
        # columns[0].write(entity['Text'])
        # columns[1].checkbox('asdf',key=f'{config.SECTIONS[index]}-{i}')
        Entities[config.SECTIONS[index]].append(entity)
        Entities[config.SECTIONS[index]][-1]['enable'] = True
        checked = st.checkbox(entity['Text'],key=f'{config.SECTIONS[index]}-{i}', value=True)
        Entities[config.SECTIONS[index]][-1]['enable'] = checked
        
        # Temp patch for rubric compatability
        Entities[config.SECTIONS[index]][-1]['meldogramAttributes'] = {}
        Entities[config.SECTIONS[index]][-1]['meldogramAttributes']['weight'] = 1
        Entities[config.SECTIONS[index]][-1]['meldogramAttributes']['negated'] = 1
        Entities[config.SECTIONS[index]][-1]['meldogramAttributes']['category'] = entity['Category']
        
    st.write("Missing an item? Some items are not accurately detected by the AI. If you are missing an item, please edit your rubric and re-run it as appropriate")
    
    return Entities
    
    
@st.cache_data
def beautify_note(txt):
    txt = re.sub(r'(Problem \d+:)', r'<br><br>\r ##### \1', txt)
    txt = re.sub(r'(Differential DX:)', r'##### \1', txt)
    txt = re.sub(r'(Diagnostic Plan:)', r'##### \1', txt)
    txt = re.sub(r'(Treatment Plan+:)', r'##### \1', txt)
    return txt

def update_grade(meld):
    overlap_sum = np.sum(meld['Overlaps Bool'])
    overlap_total = 0 # declared here in case it's an empty section
    if 'Points' in meld:
        overlap_total = meld['Points']
        if overlap_sum > overlap_total:
            overlap_sum = overlap_total
    return overlap_sum, overlap_total

@st.cache_data
def generate_base_pd_frame():
    export_data_columns = ['Terms Correct', 
                           'Terms Missed', 
                           'Points Given', 
                           'Total Points Possible', 
                           'Grade']
    
    rows = [0 for x in range(len(export_data_columns))]
    
    my_dict = {'Problem list' : rows, 
               'Differential diagnosis' : rows, 
               'Diagnostic plan' : rows, 
               'Therapeutic plan' : rows}
    
    df = pd.DataFrame.from_dict(my_dict, orient='index')
    df.columns = export_data_columns
    pd.set_option('mode.chained_assignment', None)
    
    return df

@st.cache_data
def generate_export_data(meld):
    pd_frame = generate_base_pd_frame()
    
    for major_section in meld:
        # setup some variables per section
        invert_correct = [not x for x in meld[major_section]['Overlaps Bool']]
        missed_terms = list(compress(meld[major_section]['Overlaps Text'], invert_correct))
        correct_terms = list(compress(meld[major_section]['Overlaps Text'], meld[major_section]['Overlaps Bool']))
        overlap_sum, overlap_total = update_grade(meld[major_section])
        
        # Build frame
        pd_frame['Terms Correct'][major_section] = str(f'"{"; ".join(correct_terms)}"')
        pd_frame['Terms Missed'][major_section]= str(f'"{"; ".join(missed_terms)}"')
        pd_frame['Points Given'][major_section] = overlap_sum
        pd_frame['Total Points Possible'][major_section] = overlap_total
        if overlap_total == 0:
            pd_frame['Grade'][major_section] = '0%'
        else:
            pd_frame['Grade'][major_section] = f'{str(overlap_sum / overlap_total*100)}%'
        
    return pd_frame.to_csv().encode('utf-8')