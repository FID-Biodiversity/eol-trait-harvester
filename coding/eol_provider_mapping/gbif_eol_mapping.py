# -*- coding: utf-8 -*-
"""
Mapping of eol and gbif pages
https://eol.org/
https://www.gbif.org/

using provider_ids.csv as input from 
https://opendata.eol.org/dataset/identifier-map

sources used for coding:
https://stackoverflow.com/questions/51097057/python-read-bigger-csv-line-by-line

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

    # Ein interessanter alternativer Ansatz, um die Daten vorzufiltern und anschließend zu halten: https://stackoverflow.com/a/26464901/7504509
    # Vielleicht ist aber die Library dask besser? Das müsste mal getestet werden: https://stackoverflow.com/a/61024560/7504509

    with open(source_csv_file, 'r',) as f:
        read_operation = csv.reader(f)

        # Iterate data rows
        for line in read_operation:
            if (provider_id is None or line[2] == provider_id) and line[3] == eol_page_id:
                provider_page_id = line[1]
                break

    return provider_page_id

#git push test
