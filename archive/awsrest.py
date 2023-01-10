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
import hashlib, hmac
from datetime import datetime, timezone

import boto3


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
        self.requestAWS('comprehendmedical', 'POST', '/v1/DetectEntitiesV2', 0, 0)
    
    def getSignatureKey(self, key, datestamp, region, service):
        kDate = hmac.HMAC(datestamp.encode(), ('AWS4' + key).encode(), digestmod=hashlib.sha512).hexdigest()
        kRegion = hmac.HMAC(region.encode(), kDate.encode(), digestmod=hashlib.sha512).hexdigest()
        kService = hmac.HMAC(service.encode(), kRegion.encode(), digestmod=hashlib.sha512).hexdigest()
        kSigning = hmac.HMAC("aws4_request".encode(), kService.encode(), digestmod=hashlib.sha512).hexdigest()
        return kSigning
    
    def requestAWS(self, service, method, api, postBody, objectData):
        host = service + "." + self._region + ".amazonaws.com"
        endpoint  = "https://" + host + api
        request_parameters = "LanguageCode=en-US"
        amz_date = datetime.now(timezone.utc)
        datestamp = amz_date.strftime('%Y%m%d');
        amz_date = amz_date.strftime("%a, %d %b %G %T %Z")
        
        # Building request
        canonical_headers = "host:" + host + "\n"
        signed_headers = "host"
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = datestamp + "/" + self._region + "/" + service + "/" + "aws4_request"
        canonical_querystring = request_parameters
        canonical_querystring = canonical_querystring + "&X-Amz-Algorithm=AWS4-HMAC-SHA256";
        canonical_querystring = canonical_querystring+ "&X-Amz-Credential=" + self._accessKey + "/" + credential_scope # .replace("/", "%2F")
        canonical_querystring = canonical_querystring+ "&X-Amz-Date=" + amz_date
        canonical_querystring = canonical_querystring+ "&X-Amz-Expires=30";
        canonical_querystring = canonical_querystring+ "&X-Amz-SignedHeaders=" + signed_headers;
        
        payload_hash = hashlib.sha256("".encode())
        canonical_request = method + "\n" + api + "\n" + canonical_querystring + "\n" + canonical_headers + "\n" + signed_headers + "\n" + payload_hash.hexdigest()
        string_to_sign = algorithm + "\n" +  amz_date + "\n" +  credential_scope + "\n" + hashlib.sha256(canonical_request.encode()).hexdigest()
        signing_key = self.getSignatureKey(self._secretKey, datestamp, self._region, service);
        signature = hmac.HMAC(string_to_sign.encode(), signing_key.encode(), digestmod=hashlib.sha512).hexdigest()
        canonical_querystring += "&X-Amz-Signature=" + signature;
        response = requests.post(endpoint + "?" + canonical_querystring);
        if(response.ok):
        
            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            print('')
        else:
          # If response code is not ok (200), print the resulting http error code with description
            response.raise_for_status()
            
# AWS = AWSRest()
