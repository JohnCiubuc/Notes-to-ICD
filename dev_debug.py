#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 20:00:36 2023

@author: inathero
"""
import re
import bisect
a = ['this', ('a', 'list'), 'is a', ('list')]

for i in a:
    print(type(i))
    
    

complex_thresholds = [0,0.6,0.85]
a= bisect.bisect(complex_thresholds, 0.8)
a = [1,2,3]
b = ['a','b','c']
d = zip(a,b)