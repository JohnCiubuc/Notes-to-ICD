#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 9 12:18:26 2023

@author: John Ciubuc
"""
import aws
import re


f = open('DID_Notes/DID1.txt')
note = f.read()

# Reformat note to only send the sections relevant to be NLP'd
# specifically, HPI and A&P
# Note format must be known in advanced.
clip_sections = [('Reason For Visit', 'Review of Systems'), ('Assessment', 'END')]

note_sections = []
for section in clip_sections:
    start = note.find(section[0])
    end = note.find(section[1]) if section[1] != 'END' else -1
    note_sections.append(note[start:end])    

# response = comp.detect_entities(Text='Encounter for wellness examination in adult. Patient has a complex renal cyst')
# response = aws.detectEntities(note)

# a = response['Entities']
# for entity in a:
#     print('Entity', entity)
