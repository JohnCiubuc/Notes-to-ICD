#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 9 12:18:26 2023

@author: John Ciubuc
"""
from . import aws, snomed, acronyms
import pickle
import re

#  ===============================
#  ========== DEBUG ==============
#  ===============================
DEBUG_USE_PICKLE = False
#  ===============================
#  ===============================
#  ===============================

ICD_CONFIDENCE = 0.1
ENT_CONFIDENCE = 0.1
note = ''
note_section_indexes = ''
# If changed, update qt_meldogram's list
# clip_sections = [('History of Presenting Illness', 'Physical Exam'), ('Physical Exam', 'Assessment and Plan'), ('Assessment and Plan', 'Diagnostic Studies'), ('Diagnostic Studies', 'END')]
clip_sections = [('Problem list', 'Differential diagnosis'), 
                 ('Differential diagnosis', 'Diagnostic plan'), 
                 ('Diagnostic plan', 'Therapeutic plan'), 
                 ('Therapeutic plan', 'END')]

regex_sections = ['Problem \d:(.*?)Differential',
                  'Differential DX:(.*?)Diagnostic',
                  'Diagnostic Plan:(.*?)Treatment',
                  'Treatment Plan:(.*?)Problem'] # you have to manually check last treatmet plan
SECTIONS = ['Problem list', 'Differential diagnosis', 'Diagnostic plan', 'Therapeutic plan']



# Reformat note to only send the sections relevant to be NLP'd
# specifically, HPI and A&P
# Note format must be known in advanced.
# Sections added in list rather than appending for processing later
    
def set_sections_on_clips(note, is_student_note = True):
    note_lower = note.lower()
    if not is_student_note:
        note_sections = []
        for section in clip_sections:
            start = note_lower.find(section[0].lower())
            end = note_lower.find(section[1].lower()) if section[1] != 'END' else -1
            note_sections.append(note[start:end])   
    else:    
        note_sections = {}
        for i, n in enumerate(regex_sections):
            pattern = re.compile(n, re.M|re.S)
            matches = [x.strip() for x in pattern.findall(note)]
            if i == len(regex_sections)-1:
                r_index = note.rfind('Treatment Plan:')
                matches.append(note[r_index+len('Treatment Plan:'):-1].strip())
            print(matches)
            note_sections[SECTIONS[i]] = matches
    return note, note_sections    




def recombine_for_aws(note_sections):
    # Recombine sections for aws
    # Count each section size for processing
    note = ''
    # Rubric note
    if type(note_sections) == list:
        note_section_indexes = []
        for section in note_sections:
            note = note + section + '\n'
            if len(note_section_indexes) > 0:
                note_section_indexes.append(note_section_indexes[-1] + len(section))
            else: 
                note_section_indexes.append(len(section))
        note_section_indexes.append(len(note))
    # Student Note
    else:
        note_section_indexes = {}
        # Disgusting and unsafe
        try:
            big_list = list(note_sections.items())
            unlabeled_index_list = []
            labeled_index_list = {}
            for i in range (0, len(big_list[0][1])):
                section = ''
                for x in range (0, len(SECTIONS)):
                    section = section + big_list[x][0] + ':\r\n\r\n\t'
                    section = section + big_list[x][1][i] + '\r\n\r\n'
                section = section + '\r\n------------------\r\n'
                note = note + section
            for i in range(0, len(SECTIONS)):
                indexes = [m.start() for m in re.finditer(SECTIONS[i],note)]
                unlabeled_index_list.extend(indexes)
                labeled_index_list[SECTIONS[i]] = indexes
            note_section_indexes['unlabeled_index_list'] = unlabeled_index_list
            note_section_indexes['labeled_index_list'] = labeled_index_list
            
        except:
            print('Warning.. ran out of range in recombine for aws function. Please contact the developer for fixing')
    
    
    return (note,note_section_indexes)



def readNote_Debug():
    f = open('DID_Notes/DID1.txt')
    note = f.read()
    return set_sections_on_clips(note)

    
def request_amazon(note):
    entities = {}
    # Request entities
    if DEBUG_USE_PICKLE:
        file = open('aws_response.pkl', 'rb')
        entities = pickle.load(file)
        file.close()
    else:
        # response = aws.detectICDs(note)
        # entities['ICD']  = response['Entities']
        # response = aws.detect_entities(note)
        # entities['ENT']  = response['Entities']
        # response = aws.detect_snomed(note)
        # entities['SNO']  = response['Entities']
        response = aws.detect_snomed(note)
        entities['ENT']  = response['Entities']

    # save to not abuse api while testing
    # file = open('aws_response.pkl', 'wb')
    # pickle.dump(entities, file)
    # file.close()
    
    return entities

def prune_entities_to_confidence(entities):
    # Prune entities per confidence
    e_list_high = []
    e_list_low = []
    for e in entities:
        #  Raw entity detection is valid
        if e['Score'] > ICD_CONFIDENCE:
            # Raw ICD code connection is valid
            # This is an ICD code
            if 'ICD10CMConcepts' in e:
                try:  
                    if len(e['ICD10CMConcepts']) > 0:
                        if e['ICD10CMConcepts'][0]['Score'] > ICD_CONFIDENCE:
                            e_list_high.append(e)
                        else:
                            e_list_low.append(e)
                            continue
                except:
                    print('error')
            # This is an entity
            else:
                if e['Score'] > ENT_CONFIDENCE:                            
                    e_list_high.append(e)
                else:
                    e_list_low.append(e)
                    continue
                
    return e_list_low, e_list_high

def reformat_entities_to_section(entities, note_section_indexes):
    entity_sections = {}
    # Reformat entities per section
    for entity in entities:
        begin_offset = entity['BeginOffset']
        # Rubric
        if type(note_section_indexes) == list:
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
        # Student Note        
        else:
            labeled     = note_section_indexes['labeled_index_list']
            unlabeled   = note_section_indexes['unlabeled_index_list']
            for section_name in labeled:
                if max(b for b in unlabeled if b < begin_offset) in labeled[section_name]:
                    if section_name in entity_sections:
                        entity_sections[section_name].append(entity)
                    else:
                        entity_sections[section_name] = [entity]
    return entity_sections



# note, note_sections = readNote_Debug()
# note, note_section_indexes = recombine_for_aws(note_sections)
# entities = request_amazon();
# entities = prune_entities_to_confidence(entities)
# entity_sections = reformat_entities_to_section(entities)


# debug = []
# print("\n\nObtained from HPI:")
# for ents in entity_sections['Reason For Visit']:
#     # print(ents['Text'])
#     ents['Text'] =  acronyms.fixAncronyms(ents['Text'])
#     print(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
#     debug.append(snomed.getICD(ents['Text']))
    
    
# print("\n\nObtained from Assessment and Plan:")
# for ents in entity_sections['Assessment']:
#     # print(ents['Text'])
#     ents['Text'] =  acronyms.fixAncronyms(ents['Text'])
#     print(f"{ents['Text']} ({ents['ICD10CMConcepts'][0]['Description']}) - {ents['ICD10CMConcepts'][0]['Code']}")
#     debug.append(snomed.getICD(ents['Text']))
