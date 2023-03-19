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
from modules import snomed
from itertools import compress

# Taken from https://stackoverflow.com/a/50784012/19491646
import matplotlib as mpl

def color_fader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


def reconstitute_paragraph_gen(reconst_list, entity, score):
    """
    Takes a reconst list, finds an entity, replaces it with tuple for
    annotated_text extension

    Parameters
    ----------
    reconst_list : LIST
        WIP reconst list.
    entity : STR
        Name of entity to replace.
    score : FLOAT
        Score used for color gradiemnt.

    Returns
    -------
    reconst_list : LIST
        WIP reconst list.

    """
    
    for el in reconst_list:
        if type(el) == str:
            split = el.split(entity)
            # Failed split, entity does not exist
            if len(split) == 0:
                yield el
            
            # Return pre-string
            yield split[0]
            for split_i in range(1,len(split)):
                if score == -1:
                    yield (entity, 'N/A', '#800080')
                else:
                    yield (entity, f'{score*100:.2f}', color_fader('red', 'green', score))
                yield split[split_i]
        else:
            yield el

@st.cache_data
def generate_annotated_paragraph(note_section, entity_list):
    """
    

    Parameters
    ----------
    note_section : STR
        Full paragraph section.
    entity_list : LIST
        Entity list from aws. Contains dict of format: [str, list]

    Returns
    -------
    reconst : LIST
        List for annotated_text.
    scores : TYPE
        DESCRIPTION.
    texts : TYPE
        DESCRIPTION.

    """
    reconst = [note_section]
    scores = []
    texts = []
    codes = []
    print('\n\n')
    # st.write(entity_list)
    for entity in entity_list:
        # Generate specificty score
        # Try ICD name first
        for icd_value in entity[list(entity.keys())[0]]:
            # st.write(icd_value)
            snomed_code = snomed.snomed_code(icd_value['Description'])
            if snomed_code != -1:
                break
        
        # Try note text next[0]
        if snomed_code == -1:
            snomed_code = snomed.snomed_code(list(entity.keys())[0])
        # Failed both
        if snomed_code == -1:
            score = -1
        # Pass for both (what a weird cascade)
        else:
            score = snomed.snomed_specificity_score(snomed_code)
            
        # Yeah i know i should collapse this all into one var
        scores.append(score)
        texts.append(list(entity.keys())[0])
        codes.append(snomed_code)
        
        # Split string
        reconst = list(reconstitute_paragraph_gen(reconst, list(entity.keys())[0], score))

    return reconst, scores, texts, codes