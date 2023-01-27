# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 10:54:49 2022

@author: AHMAD
"""
import logging
import pathlib
from typing import List, Optional, Set, Union

from eol.conversions import IdentifierConverter
from eol.data import DataProvider, read_csv_file
from eol.handlers import DataHandler
from eol.normalization import Normalizer
from eol.triple_generator import Triple, TripleGenerator, deduplicate_triples


class EncyclopediaOfLifeProcessing:
    """The main interface for retrieving EOL data."""

    RELEVANT_DATA_PROVIDERS = [DataProvider.Gbif]

    def __init__(
        self,
        data_handler: DataHandler,
        data_normalizer: Normalizer,
        data_provider_mapping_csv_file_path: pathlib.Path = None,
    ):
        self.data_handler = data_handler
        self.data_normalizer = data_normalizer
        self.identifier_converter = None

        if data_provider_mapping_csv_file_path is not None:
            self.identifier_converter = IdentifierConverter(
                data_provider_mapping_csv_file_path, self.RELEVANT_DATA_PROVIDERS
            )

        self.logger = logging.getLogger(__name__)

    def get_gbif_id_for_eol_page_id(
        self, eol_page_id: Union[str, int]
    ) -> Optional[str]:
        """Returns the corresponding GBIF species ID for a given EOL page ID.

        If no corresponding GBIF ID can be found, None is returned.

        :raises IdentifierConverterNotSetError: If the identifier converter is not set.
        """
        if self.identifier_converter is None:
            raise IdentifierConverterNotSetError(
                "You have to provide a data provider mapping CSV file!"
            )

        self.logger.debug(f"Converting EOL ID {eol_page_id} to GBIF ID...")

        return self.identifier_converter.from_eol_page_id(
            eol_page_id, DataProvider.Gbif
        )

    def get_eol_page_id_from_gbif_id(self, gbif_id: Union[str, int]) -> str:
        """Returns the corresponding EOL page ID for a given GBIF ID.
        :raises IdentifierConverterNotSetError: If the identifier converter is not set.
        """
        if self.identifier_converter is None:
            raise IdentifierConverterNotSetError(
                "You have to provide a data provider mapping CSV file!"
            )

        self.logger.debug(f"Converting GBIF ID {gbif_id} to EOL ID...")

        return self.identifier_converter.to_eol_page_id(gbif_id, DataProvider.Gbif)

    def get_trait_data_for_eol_page_id(
        self,
        eol_page_id: str,
        filter_for_predicates: Set[
            str
        ] = None,  # filter for results in triples. None for no filter
    ) -> List[Triple]:  # function returns list of triple objects
        """Returns a list of Triple objects containing trait data for the given EOL
        page ID.

        The returned list are only traits directly related to the taxon associated
        with the given EOL page ID.

        If given `filter_for_predicates`, all returned Triple objects are restricted
        to the given predicate URIs. (e.g.
        {"http://rs.tdwg.org/dwc/terms/habitat", "http://eol.org/schema/terms/Present"}
        ).
        """

        triples = set()
        triple_generator = TripleGenerator()
        for non_normalized_data in self.data_handler.iterate_data_by_key(
            key="page_id", value=int(eol_page_id)
        ):
            normalized_data = self.data_normalizer.normalize(non_normalized_data)
            generated_triples = triple_generator.create_triples(normalized_data)
            triples.update(generated_triples)

        filtered_triples = filter_triples_for_predicates(triples, filter_for_predicates)
        return deduplicate_triples(filtered_triples)


def filter_triples_for_predicates(
    triples: Set[Triple], filter_for_predicates: Set[str]
) -> Set[Triple]:
    """Returns a list containing only Triples that have a predicate
    that was given in `filter_for_predicates`.
    If `filter_for_predicates` is None or an empty list, the original list of Triples
    is returned.
    """
    filtered_triples = triples
    if filter_for_predicates is not None and filter_for_predicates:
        filtered_triples = {
            triple for triple in triples if triple.predicate in filter_for_predicates
        }
    return filtered_triples


class IdentifierConverterNotSetError(Exception):
    """Should be raised when the IdentifierConverter is called but is set to None."""
