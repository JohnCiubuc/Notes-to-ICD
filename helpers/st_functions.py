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

def _reconstitute_paragraph(reconst_list, entity, score):
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
    
    
    
    
    return reconst_list

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
    reconst = []
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