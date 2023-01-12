#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 17:11:16 2022

@author: inathero
"""
import os.path
import pickle
import re
ancronymList = {}
database = os.path.dirname(__file__) + "/ancronymDatabase.db"

if os.path.exists(database):
    with open(database, 'rb') as handle:
        ancronymList = pickle.load(handle)
        handle.close()

def fixAncronyms(text):
    for item in ancronymList:
        reg = re.compile(re.escape(item), re.IGNORECASE)
        text = reg.sub(ancronymList[item], text)
    return text

# don't forget to run this function after modifying it
def createAncronymDatabase():
    ancronymList['U/S'] = "ultrasound"
    ancronymList['N/V'] = "nausea and vomiting"
    ancronymList['r/o'] = "rule out"
    ancronymList['2/2'] = "secondary to"
    ancronymList['y/o'] = "year old"
    ancronymList['LMP'] = "last menstrual period"
    ancronymList['PMHx'] = "PMH"
    ancronymList['FMHx'] = "FH"
    ancronymList['FamHX'] = "FH"
    ancronymList['Family history'] = "FH"
    ancronymList['wt'] = "weight"
    ancronymList['bp'] = "blood pressure"
    os.remove(database)
    with open(database, 'wb') as handle:
        pickle.dump(ancronymList, handle)
        handle.close()        
        
# createAncronymDatabase()