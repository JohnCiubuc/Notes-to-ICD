#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 17:12:09 2023

@author: inathero
"""
# from pymedtermino import *
from pymedtermino.snomedct import SNOMEDCT
from pymedtermino.icd10 import ICD10,ICD10Concept


# a=SNOMEDCT.search('insomnia')

def search(text):
    return SNOMEDCT.search(text)

def getICD(snomedCode):
    return ICD10.search(snomedCode)

# b = getICD('insomnia')
# print(b)
# getICD(8943002)
# a=ICD10.search('weight gain')
# b=ICD10Concept(8943002)