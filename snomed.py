#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 17:12:09 2023

@author: inathero
"""

# from pymedtermino import *
from pymedtermino.snomedct import SNOMEDCT

# a=SNOMEDCT.search('insomnia')

def search(text):
    return SNOMEDCT.search(text)
