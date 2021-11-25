# -*- coding: utf-8 -*-
"""
EoL Trait Data

using the following csv files as input from
https://editors.eol.org/other_files/SDR/traits_all.zip 
pages.csv
traits.csv

trait scheme explanation:
https://github.com/EOL/eol_website/blob/master/doc/trait-schema.md

"""

__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, \
                 Senckenberganlage 25, 60325 Frankfurt, Germany"

import csv #csv read in automatically as str

def eol_trait_data(eol_page_id:str):
    # input eol_page_id
    eol_page_id = str(eol_page_id)#convert input always as str

    # change the name of your files here
    # enter the whole address if files are not in same folder
    pages_file = "pages.csv"
    traits_file = "traits.csv"
    
def predicate():
    



