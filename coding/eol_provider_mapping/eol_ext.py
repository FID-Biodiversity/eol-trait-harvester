# -*- coding: utf-8 -*-
"""
EOL-data-extraction

@author: TAHIR
"""

import pandas as pd

#traitsfile = "test_traits.csv"

"""
def get_ids(eol_page_id, provider_id):
    eol_page_id = input("Eingabe der eol_page_id: ")
    provider_id = input("Eingabe der provider_id: ")
"""


def search_eol(traitsfile, eol_page_id, provider_id):#type in filename after execution of this file
    print("Suche: ", eol_page_id, provider_id)#only for testing
    chunksize = 8
    for chunk in pd.read_csv(traitsfile, chunksize=chunksize):
        #i = chunk
        #i = 1
        #print('type: %s shape  %s' % (type(chunk), chunk.shape)) #größe der chunks und wieviele
        #dtype
        print(chunk)
        if "resource_id" == provider_id:
            if "page_id" == eol_page_id:
                print("True")
                #row_true = zeilennummer
                #halte predicate fest

def take_predicate(row_true):
#take "predicate" from row_true:
    if gbif_df.loc[gbif_df['predicate'] == 'http://eol.org/schema/terms/Present']:
        #go for geographic distribution

    if gbif_df.loc[gbif_df['predicate'] == 'http://purl.obolibrary.org/obo/RO_0002303']:
        #go for habitat
        
def take_object(row_true):
    #take "arrow" depend on predicate
    #end_object = 


result_array = []
result_array.append(end_subject)
result_array.append(end_predicate)
result_array.append(end_object)

return result_array
                

         
