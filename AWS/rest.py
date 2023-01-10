#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 12:18:26 2023

@author: John Ciubuc

Adapted from https://github.com/johnCiubuc/QtPolly
"""
import requests
import os
import configparser
from datetime import datetime, timezone

class AWSRest:
    _accessKey=''
    _secretKey=''
    _region = "us-east-2"
    _endpoint = "apigateway.us-west-1.amazonaws.com"
    
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~") + '/.aws/credentials')
        self._accessKey = config.get('default','aws_access_key_id') 
        self._secretKey = config.get('default','aws_secret_access_key') 
        self.requestAWS('comprehend', 'POST', '/v1/comprehend', 0, 0)
        
    def requestAWS(self, service, method, api, postBody, objectData):
        host = service + "." + self._region + ".amazonaws.com"
        endpoint  = "https://" + host + api
        request_parameters = "LanguageCode=en-US"
        amz_date = datetime.now(timezone.utc)
        datestamp = amz_date.strftime('%Y%m%d');