# -*- coding: utf-8 -*-
"""
Mapping of eol and gbif pages
https://eol.org/
https://www.gbif.org/

using provider_ids.csv as input from 
https://opendata.eol.org/dataset/identifier-map

sources used for coding:
https://stackoverflow.com/questions/51097057/python-read-bigger-csv-line-by-line

last update: 23-09-2021
"""
__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, \
                 Senckenberganlage 25, 60325 Frankfurt, Germany"


import pandas as pd
#import csv
#import time // REMOVE TO SHOW TIME

#def eol_provider_mapping_pd(eol_page_id: str, provider_id: str):
    
    #eol_page_id = str(eol_page_id)#convert input always as str
    #provider_id = str(provider_id)#convert input always as str
    
    # change the name of your file here
    # enter the whole address if file is not in same folder
datafile = "test_provider_ids.csv"

readfile = pd.read_csv(datafile)
    #print(readfile)
here = readfile.loc[readfile["resource_id"] == "767"]
print(here)

#Problem mit der typ-Ausgabe
#noch zu beheben