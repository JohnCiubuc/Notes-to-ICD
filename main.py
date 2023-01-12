#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 9 12:18:26 2023

@author: John Ciubuc
"""
import aws

# a=SNOMEDCT.search('insomnia')

f = open('DID_Notes/DID1.txt')
note = f.read()

f = open('DID_Notes/DID1.txt')
note = f.read()

# Reformat note to only send the sections relevant to be NLP'd
# specifically, HPI and A&P
# Note format must be known in advanced.

clip_sections = [('Reason For Visit', 'Review of Systems'), ('Assessment', 'END')]


# response = comp.detect_entities(Text='Encounter for wellness examination in adult. Patient has a complex renal cyst')
response = aws.detectEntities(note)

a = response['Entities']
for entity in a:
    print('Entity', entity)
