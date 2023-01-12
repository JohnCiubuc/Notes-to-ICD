#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 9 12:18:26 2023

@author: John Ciubuc
"""
import aws
import snomed
import acronyms
import pickle

#  ===============================
#  ========== DEBUG ==============
#  ===============================
DEBUG_USE_PICKLE = True
#  ===============================
#  ===============================
#  ===============================


f = open('DID_Notes/DID1.txt')
note = f.read()

# Reformat note to only send the sections relevant to be NLP'd
# specifically, HPI and A&P
# Note format must be known in advanced.
# Sections added in list rather than appending for processing later
clip_sections = [('Reason For Visit', 'Review of Systems'), ('Assessment', 'END')]
note_sections = []
for section in clip_sections:
    start = note.find(section[0])
    end = note.find(section[1]) if section[1] != 'END' else -1
    note_sections.append(note[start:end])   
    


# Recombine sections for aws
# Count each section size for processing
note = ''
note_section_indexes = []
for section in note_sections:
    note = note + section + '\n'
    if len(note_section_indexes) > 0:
        note_section_indexes.append(note_section_indexes[-1] + len(section))
    else: 
        note_section_indexes.append(len(section))
note_section_indexes.append(len(note))

# Request entities
if DEBUG_USE_PICKLE:
    file = open('aws_response.pkl', 'rb')
    response = pickle.load(file)
    entities  = response['Entities']
    file.close()
else:
    response = aws.detectEntities(note)
    entities  = response['Entities']

# save to not abuse api while testing
file = open('aws_response.pkl', 'wb')
pickle.dump(response, file)
file.close()

entity_sections = {}
# Reformat entities per section
for entity in entities:
    begin_offset = entity['BeginOffset']
    for name,index in enumerate(note_section_indexes):
        if begin_offset > index:
            continue
        else:
            section_name = clip_sections[name][0]
            if section_name in entity_sections:
                entity_sections[section_name].append(entity)
            else:
                entity_sections[section_name] = [entity]
            break
    
debug = []
for ents in entity_sections['Reason For Visit']:
    print(ents['Text'])
    debug.append(snomed.search(ents['Text']))
a = snomed.search('weight gain')
# for entity in a:
#     print('Entity', entity)
