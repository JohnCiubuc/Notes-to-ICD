#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 15:02:51 2023

@author: John Ciubuc
"""

import os
import glob

FOLDER_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

# RUBRICS = ['case_x', 'case_y','rubric']

# def update_rubrics():
#     RUBRICS = glob.glob(FOLDER_PATH+'pickles/editor/*.pckl')
#     return [os.path.splitext(os.path.basename(x))[0] for x in RUBRICS]

# RUBRICS = update_rubrics()

# If changed, update qt_meldogram's list
# clip_sections = [('History of Presenting Illness', 'Physical Exam'), ('Physical Exam', 'Assessment and Plan'), ('Assessment and Plan', 'Diagnostic Studies'), ('Diagnostic Studies', 'END')]
CLIP_SECTIONS = [('Reason For Visit', 'Review of Systems'), 
                 ('Review of Systems', 'Past Medical History'), 
                 ('Physical Exam', 'Assessment'), 
                 ('Assessment', 'END')]

REGEX_SECTIONS = ['Problem \d:(.*?)Differential',
                  'Differential DX:(.*?)Diagnostic',
                  'Diagnostic Plan:(.*?)Treatment',
                  'Treatment Plan:(.*?)Problem'] # you have to manually check last treatmet plan

SECTIONS = ['Reason For Visit', 'Review of Systems', 'Past Medical History', 'Physical Exam', 'Assessment and Plan']