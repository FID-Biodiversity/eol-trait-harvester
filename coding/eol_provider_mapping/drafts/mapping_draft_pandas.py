# -*- coding: utf-8 -*-
"""
EncyclopediaOfLiveProcessing.py

Mapping of eol and gbif pages
https://eol.org/
https://www.gbif.org/

sources used for coding: ###

last update: 13-09-2021
"""
__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, Senckenberganlage 25, 60325 Frankfurt, Germany"


import pandas as pd

datafile = "test_provider_ids.csv"

#read in
providerfile = pd.read_csv(r"C:\Users\AHMAD\Desktop\TextAnnotation\GBIF\testing_gbif\provider_ids.csv", \
dtype={"node_id": int, "resource_pk": int, "resource_id": int, "page_id": int, "preferred_canonical_for_page": str})
#filter by gbif 767
output = providerfile.loc[providerfile['resource_id'] == "767"] ###recheck for log method
print(output)

