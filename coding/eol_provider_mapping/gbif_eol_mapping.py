# -*- coding: utf-8 -*-

"""
Biofid project

Mapping of eol and gbif pages
https://eol.org/
https://www.gbif.org/

using provider_ids.csv as input from 
https://opendata.eol.org/dataset/identifier-map
    
"""
__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, \
                 Senckenberganlage 25, 60325 Frankfurt, Germany"

import csv
import pathlib
from dataclasses import dataclass
from typing import Optional, Union, List
from eol import handlers, normalization #nutze STRING für triple ausgabe
from eol.triple_generator import Triple, TripleGenerator
from eol.normalization import EolTraitCsvNormalizer
from eol.handlers import EolTraitCsvHandler


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
        handler = EolTraitCsvHandler('../tests/data/test_eol_traits.csv')
        non_normalized_csv_data = next(handler.iterate_data_by_key(key='page_id', value=45258442))

        # Normalize the data
        normalizer = EolTraitCsvNormalizer()
        normalized_data = normalizer.normalize(non_normalized_csv_data)

        # Generate triples
        triple_generator = TripleGenerator()
        triples = triple_generator.create_triples(normalized_data) #ausgabe der triples


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
"""
def retrn_object():
    if ...:
        ## für spalte A
    else if...:
        ## für spalte B
    else if ...:
        ##für spalte C
"""
        
#kreiere default: obj-spalten nehmen
        #und nur wenn best. predicate dann wirds umgeändert
        
#eingabe eines predicates
        
#wörterbuch funktion


