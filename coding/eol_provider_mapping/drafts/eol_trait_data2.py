# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 12:24:23 2021

@author: TAHIR
"""

import pandas as pd
#import csv

#def traits_readin():
traitslines = pd.read_csv("traits.csv", dtype = str)
gbifs = traitslines.loc[traitslines['resource_id'] == '767'] #767 durch provider_id ersetzen
#print(gbifs)#wegmachen

#def pages_readin():
pageslines = pd.read_csv("pages.csv", dtype = str)
# if eol_page_id == 'page_id'
#     return parent_id
