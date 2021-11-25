# -*- coding: utf-8 -*-
"""
Mapping of eol and gbif pages using PANDAS
https://eol.org/
https://www.gbif.org/

using provider_ids.csv as input from 
https://opendata.eol.org/dataset/identifier-map
"""
__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, \
                 Senckenberganlage 25, 60325 Frankfurt, Germany"

import pandas as pd
#import time # REMOVE TO SHOW TIME
#import csv

#start = time.time() #Laufzeitmessung Startzeit // REMOVE TO SHOW TIME

#def gbif_einlesen():
df = pd.read_csv("provider_ids.csv", dtype = str)
gbifs = df.loc[df['resource_id'] == '767'] #statt 767: provider_id
#print(gbifs) #for testing
#print()

#search for eol_page_id
organism_line = gbifs.loc[df['page_id'] == '57357772'] #Petroniptus
#print(organism_line) #for testing
#print()

#return provider(gbif)-id
provider_page_id =organism_line['resource_pk'].values[0]
print(provider_page_id)


#ende = time.time() #Endzeit // REMOVE TO SHOW TIME
#print('{:5.3f}s'.format(ende-start)) #Berechnung Laufzeit // REMOVE TO SHOW TIME

