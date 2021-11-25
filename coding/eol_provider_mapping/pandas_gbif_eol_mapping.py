# -*- coding: utf-8 -*-

"""
Biofid project

Mapping of eol and gbif pages using PANDAS
https://eol.org/
https://www.gbif.org/

using provider_ids.csv as input from 
https://opendata.eol.org/dataset/identifier-map

Version 2.0 Pandas
    
"""
__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, \
                 Senckenberganlage 25, 60325 Frankfurt, Germany"

import csv
import pathlib
from dataclasses import dataclass
from typing import Optional, Union, List


@dataclass
class Triple:
    subject: str
    predicate: str
    object: str


class EncyclopediaOfLifeProcessing:
    def __init__(self):
        self.csv_path: Optional[Union[str, pathlib.Path]] = None

    def get_gbif_id_for_eol_page_id(self, eol_page_id: Union[str, int]) -> str:
        """ Returns the corresponding GBIF species ID for a given EOL page ID. """
        gbif_provider_id = '767'
        return eol_provider_mapping(self.csv_path, eol_page_id, gbif_provider_id)

    def get_trait_data_for_eol_page_id(self, eol_page_id: str, recursive: bool = False,
                                       filter_by_predicate: List[str] = None) -> List[Triple]:
        """ Returns a list of Triple objects containing trait data for the given EOL page ID.
            The returned list are only traits directly related to the taxon associated with the given EOL page ID.
            When `recursive` is True, the returned list contains traits for both the taxon associated with the given
            EOL page ID and all lower hierarchical species recursively.
        """
        pass


def eol_provider_mapping(source_csv_file: str, eol_page_id: Union[str, int], provider_id: Optional[str] = None):
    
    eol_page_id = str(eol_page_id)
    provider_id = str(provider_id)

    #filter by provider_id
    df = pd.read_csv("test_provider_ids.csv", dtype = str)
    gbifs = df.loc[df['resource_id'] == provider_id]

    #get line of organism
    organism_line = gbifs.loc[df['page_id'] == eol_page_id]

    #get provider-page-id (gbif-id)
    provider_page_id = organism_line['resource_pk'].values[0]

    return provider_page_id
