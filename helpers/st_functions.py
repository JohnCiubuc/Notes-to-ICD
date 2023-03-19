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

def replace_item(the_list):
    for item in the_list:
        if item == 'b':
            yield 'd'
            yield 'e'
        else:
            yield item

def _reconstitute_paragraph_gen(reconst_list, entity, score):
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
                yield (entity, "0.543", "#8ef")
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
        Entity list from aws.

    Returns
    -------
    reconst : LIST
        List for annotated_text.

    """
    reconst = [note_section]
    for entity in entity_list:
        # Generate specificty score
        snomed_code = snomed.snomed_code(entity)
        if snomed_code != -1:
            score = snomed.snomed_specificity_score()
        else:
            score = 0
        
        # Split string
        reconst = _reconstitute_paragraph(reconst, entity, score)

    return reconst