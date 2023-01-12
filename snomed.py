#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 17:12:09 2023

@author: inathero
"""
# from pymedtermino import *
from pymedtermino.snomedct import SNOMEDCT
from pymedtermino.icd10 import ICD10
SNOMEDCT_DIR = "/home/jiba/telechargements/base_med/SnomedCT_Release_INT_20130731"
SNOMEDCT_CORE_FILE = "/home/jiba/telechargements/base_med/SNOMEDCT_CORE_SUBSET_201308.txt"
ICD10_DIR = "/home/jiba/telechargements/base_med/icd10"
CIM10_DIR = "/home/jiba/telechargements/base_med/cim10"

# a=SNOMEDCT.search('insomnia')

def search(text):
    return SNOMEDCT.search(text)

def getICD(snomedCode):
    return ICD10[snomedCode]