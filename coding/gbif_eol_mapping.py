# -*- coding: utf-8 -*-
"""
Mapping of eol and gbif pages
https://eol.org/
https://www.gbif.org/

using provider_ids.csv as input from 
https://opendata.eol.org/dataset/identifier-map

sources used for coding:
https://stackoverflow.com/questions/51097057/python-read-bigger-csv-line-by-line

last update: 20-09-2021

###########################
passing pytests:
# Test passed: if eol_page_id or/and provider_id is not valid than print
              empty result
# Test passed: enter eol_page_id and program gives correct output of
               gbif_id or other provider_page_id based on the provider_id input
    
"""
__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, \
                 Senckenberganlage 25, 60325 Frankfurt, Germany"

import csv #csv read in automatically as str
#import time // REMOVE TO SHOW TIME


# input eol_page_id and provider_id
eol_page_id = input("Bitte geben Sie die eol_page_id ein: \n")
provider_id = input("Bitte geben Sie die provider_id ein: \n")

# change the name of your file here
# enter the whole address if file is not in same folder
datafile = "provider_ids.csv"

# read in provider_ids.csv file
#start = time.time() #Laufzeitmessung Startzeit // REMOVE TO SHOW TIME
with open(datafile, 'r',) as f:
    read_operation = csv.reader(f)
    for line in read_operation: #each line as datatype list with elements
        if line[2] == provider_id:
            if line[3] == eol_page_id:
                #print(line)
                organism_name = line[4]
                provider_page_id = line[1]
                break
                print("\nDas Lebewesen heißt", organism_name, "\nDie dazugehörige \
GBIF_page_id lautet", provider_page_id)
                
print()
    
#ende = time.time() #Endzeit // REMOVE TO SHOW TIME
#print('{:5.3f}s'.format(ende-start)) #Berechnung Laufzeit // REMOVE TO SHOW TIME
                
                