#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:42:36 2023

@author: John Ciubuc
"""
import boto3
import os
import configparser
config = configparser.ConfigParser()
config.read(os.path.expanduser("~") + '/.aws/credentials')

boto3.Session(aws_access_key_id=config.get('default','aws_access_key_id') ,                     
              aws_secret_access_key=config.get('default','aws_secret_access_key') ,
              region_name='us-east-2')

comp = boto3.client('comprehendmedical')


def detectEntities(text):
    return comp.detect_entities(Text=text)