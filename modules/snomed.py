#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 17:20:39 2022

@author: inathero
"""


# from pymedtermino import *
import streamlit as st
from pymedtermino.snomedct import SNOMEDCT


MINIMAL_CONFIDENCE_SCORE = 0.3

def snomed_debug(boolean, c1, c2):
    print(f"{c1['Text']} and {c2['Text']} are {boolean}")

def snomed_concept_is_part(concept_one, concept_two):
    bOverlap = False
    
    # Only compare if snomed concepts exist
    if 'SNOMEDCTConcepts' in concept_one and 'SNOMEDCTConcepts' in concept_two:
        
        for i, snow_concept_one in enumerate(concept_one['SNOMEDCTConcepts']):
            # Always try the first concept. Later concepts, only if greater than confidence score
            #print(f'trying concepts one: {snow_concept_one["Description"]}')
            if i > 0 and snow_concept_one['Score'] < MINIMAL_CONFIDENCE_SCORE:
                 continue
            # Try if code is valid
            if SNOMEDCT.has_concept(snow_concept_one['Code']):
                snow_item_one = SNOMEDCT[snow_concept_one['Code']]
            else:
                #print(f'concept_one, {concept_one["Text"]}, {snow_concept_one["Description"]} -{snow_concept_one["Code"]}  is invalid')
                continue
            for n,snow_concept_two in enumerate(concept_two['SNOMEDCTConcepts']):
                #print(f'trying concepts two: {snow_concept_two["Description"]}')
                # Always try the first concept. Later concepts, only if greater than confidence score
                if n > 0 and snow_concept_two['Score'] < MINIMAL_CONFIDENCE_SCORE:
                    continue
                # Try if code is valid
                
                if SNOMEDCT.has_concept(snow_concept_two['Code']):
                    snow_item_two = SNOMEDCT[snow_concept_two['Code']]
                else:
                    continue
                #else:
                #    print(f'concept_two, {concept_two["Text"]}, {snow_concept_two["Description"]} is invalid')
                    
                try:
                    bOverlap = snow_item_one.is_part_of(snow_item_two)
                except:
                    bOverlap
                    # print("relationship error")
                if bOverlap:
                    #snomed_debug(True, concept_one, concept_two)
                    return True
                try:
                    bOverlap = snow_item_two.is_part_of(snow_item_one)
                except:
                    bOverlap
                if bOverlap:
                    #snomed_debug(True, concept_two, concept_one)
                    return True
    
    #snomed_debug(bOverlap, concept_one, concept_two)
    return bOverlap

# prob = ['Hypercalcemia','Dehydration', 'hypernatremia', 'AKI', 'Hyperkalemia', 'high anion gap metabolic acidosis', 'Normocytic anemia',
# 'Isolated ALP elevation','Elevated globulin gap','Neuropathy','Anorexia', 'cachexia']


def snomed_root(snomed_code):
    snomed_hierarchy = [snomed_code]
    if not SNOMEDCT.has_concept(snomed_code):
        print('Warning: snomed_term not found in SNOMEDCT. SNOMED Root is unavailable')
        return snomed_hierarchy
    
    entity = SNOMEDCT[snomed_code]
    while len(entity.parents) > 0:
        code_parents = [x.code for x in entity.parents]
        snomed_hierarchy.append(min(code_parents))
        entity = SNOMEDCT[snomed_hierarchy[-1]]
    return snomed_hierarchy

def snomed_depth(snomed_code, child_recursion = False):
    """
    

    Parameters
    ----------
    snomed_code : INT
        snomed code for database search.
    child_recursion : BOOL, optional
        Used for internal recursion. The default is False.

    Returns
    -------
    LIST
        List of children, if recursion depth is appropriate.
    BOOL
        True if has children
        False if recursion depth is hit

    """
    if not SNOMEDCT.has_concept(snomed_code):
        print('Warning: snomed_term not found in SNOMEDCT. SNOMED Depth is unavailable')
        return [], True
    
    
    entity = SNOMEDCT[snomed_code]
    depth = 0
    if child_recursion:
        max_child_list = [snomed_code]
    else: 
        max_child_list = []
    if len(entity.children) > 0:
        code_children = [x.code for x in entity.children]
        for child in code_children:
            child_list, null = snomed_depth(child, True)
            if len(child_list) > depth:
                depth = len(child_list)
                if child_recursion:
                    child_list.insert(0, snomed_code)
                max_child_list = child_list
    return max_child_list, True

def snomed_specificity_score(snomed_code):
    # print(snomed_code)
    if not SNOMEDCT.has_concept(snomed_code):
        print('Warning: snomed_term not found in SNOMEDCT. SNOMED Score is unavailable')
        return 0
    
    concept = SNOMEDCT[snomed_code]
    rapid_dec = sum(1 for x in concept.descendants_no_double())
    rapid_asc =sum(1 for x in concept.ancestors_no_double())
    if rapid_dec == 0:
        rapid_dec = 1
        
    rapid_ratio = rapid_asc/(rapid_dec+rapid_asc)
    # print(f'rapid descend:{rapid_dec}, rapid ascend:{rapid_asc}, ratio: {rapid_ratio}')
    # print(len(snomed_root(snomed_code)))
    return rapid_ratio
    if rapid_ratio < 0.5 or rapid_dec > 50 or rapid_dec == 1:
        return rapid_ratio

    snomed_hierarchy = snomed_root(snomed_code)
    snomed_children = snomed_depth(snomed_code)
    return len(snomed_hierarchy) / (len(snomed_children) + len(snomed_hierarchy))

def snomed_code(snomed_term):
    """
    Check if term is both in active usage, and has a valid code

    Parameters
    ----------
    snomed_term : STR
        Medical search term.

    Returns
    -------
    INT
        Code or -1.

    """
    try:
        concept = SNOMEDCT.search(snomed_term)
        if len(concept) == 0 :
            try:
                snomed_term = snomed_term.split(',')
                # for term in snomed_term:
                code = SNOMEDCT.search(snomed_term)[0]
                if code != -1:
                    return code
            except:
                return -1
        else:
            for entity in concept:
                if entity.is_in_core == 0:
                    continue
                
                if entity.code != -1:
                    return entity.code
            return -1
    except:
        return -1
    try:
        if concept[0].is_in_core == 1:
            return concept[0].code
        else:
            return -1
    except:
        return -1
    return -1
    
# concept = SNOMEDCT.search('Benign enlargement of prostate')
# print(len(concept))
# concept = SNOMEDCT.search('Insomnia')
# print(len(concept))
# concept = SNOMEDCT.search('Inadequate sleep hygiene')
# print(len(concept))
# print(snomed_specificity_score(61059009))
# concept = SNOMEDCT.search(61059009)
print(snomed_code('COVID-19'))
print(snomed_code('coronavirus'))
print(snomed_code('Disease caused by severe acute respiratory syndrome'))
# concept = SNOMEDCT[363169009] #  Inflammation of specific body organs (
# concept = SNOMEDCT[74400008] #  Appendicitis (disorder)
# concept = SNOMEDCT[302168000] #  Appendicitis (disorder)
# concept = SNOMEDCT[80891009] #  Appendicitis (disorder)
# print(snomed_root(concept[0].code))
# print(snomed_depth(concept[0].code))

# print('MELDOGRAM Entity Specificity Score:')

# sample_dict = {
# 'Heart structure (body structure)':80891009,
# 'Heart rate (observable entity)':364075005,
# 'Normal sinus rhythm (finding)':64730000,
# 'Abdominal pain (finding)':21522001,
# 'Acute abdominal pain (finding)':116290004,
# 'Tachycardia (finding)':3424008,
# 'Supraventricular tachycardia (disorder)':6456007,
# 'Appendicitis (disorder)':74400008,
# 'Acute appendicitis (disorder)':85189001,
# 'Fever (finding)':386661006,
# 'Low grade pyrexia (finding)':304213008,
# 'Postoperative fever (finding)':248450003,
# 'Umbilical structure (body structure)':78220002,
# 'Umbilical hernia (disorder)':396347007,
# 'Irreducible umbilical hernia (disorder)':196863007
#     }

# for item in sample_dict:
    # snomed_specificity_score(sample_dict[item])
    # print(f'"{item}": Specificity: {snomed_specificity_score(sample_dict[item]):.2f}')
# print(snomed_root(concept.code))
# print(snomed_depth(concept.code))

# print(f'{snomed_specificity_score(concept.code):.2f}')


# [print(SNOMEDCT.search(a)[0:5]) if len(SNOMEDCT.search(a)) > 0 else print('') for a in prob]
# # SNOMED numbers are generated from IBM's NLP
# student_concept = SNOMEDCT[13197004] 
#student_concept = SNOMEDCT[129256008] 
#print(student_concept.term)
# print(129256008 in SNOMEDCT)
# rubric_concept = SNOMEDCT[5935008]
# con1 = SNOMEDCT[301754002] #RLQ pain
# con2 = SNOMEDCT[21522001] #abdomen pain
# con3 = SNOMEDCT[27033000] #lower abdomen
# nv = SNOMEDCT[16932000] # nv
# gyn = SNOMEDCT[267011001]
# rlq_loc = SNOMEDCT[48544008]
# levo1 = SNOMEDCT[72765002]
# levo2 = SNOMEDCT[710809001]
# hypot = SNOMEDCT[40930008]

