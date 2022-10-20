# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 10:54:49 2022

@author: AHMAD
"""
import pathlib
from typing import Union, List, Optional, Set

import pandas as pd
from eol.data import read_csv_file, DataProvider
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
        data_provider_mapping_csv_file_path: pathlib.Path,
    ):
        self.data_handler = data_handler
        self.data_normalizer = data_normalizer
        self.identifier_converter = IdentifierConverter(
            data_provider_mapping_csv_file_path, self.RELEVANT_DATA_PROVIDERS
        )

    def get_gbif_id_for_eol_page_id(self, eol_page_id: Union[str, int]) -> str:
        """Returns the corresponding GBIF species ID for a given EOL page ID."""
        return self.identifier_converter.from_eol_page_id(
            eol_page_id, DataProvider.Gbif
        )

    def get_eol_page_id_from_gbif_id(self, gbif_id: Union[str, int]) -> str:
        """Returns the corresponding EOL page ID for a given GBIF ID."""
        return self.identifier_converter.to_eol_page_id(gbif_id, DataProvider.Gbif)

    def get_trait_data_for_eol_page_id(
        self,
        eol_page_id: str,
        filter_for_predicates: Set[
            str
        ] = None,  # filter for results in triples. None for no filter
    ) -> List[Triple]:  # function returns list of triple objects
        """Returns a list of Triple objects containing trait data for the given EOL page ID.
        The returned list are only traits directly related to the taxon associated with the given EOL page ID.
        If given `filter_for_predicates`, all returned Triple objects are restricted to the
        given predicate URIs. (e.g. {"http://rs.tdwg.org/dwc/terms/habitat", "http://eol.org/schema/terms/Present"}).
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


class IdentifierConverter:
    """A class for converting any provider ID into an EOL page ID."""

    CORRESPONDING_ID_ROW_NAME = "resource_pk"
    EOL_PAGE_ID_ROW_NAME = "page_id"
    DATA_PROVIDER_ID_ROW_NAME = "resource_id"
    CSV_DTYPES = {
        DATA_PROVIDER_ID_ROW_NAME: "int",
        CORRESPONDING_ID_ROW_NAME: "str",
        EOL_PAGE_ID_ROW_NAME: "int",
    }

    def __init__(
        self,
        provider_csv_file_path: Union[str, pathlib.Path],
        relevant_data_providers: Union[List[DataProvider], DataProvider] = None,
    ):

        self.provider_csv_file_path = (
            pathlib.Path(provider_csv_file_path)
            if isinstance(provider_csv_file_path, str)
            else provider_csv_file_path
        )

        if relevant_data_providers is not None:
            relevant_data_providers = (
                [relevant_data_providers]
                if isinstance(relevant_data_providers, DataProvider)
                else relevant_data_providers
            )
        else:
            relevant_data_providers = []

        self._relevant_data_providers = relevant_data_providers
        self._csv_dataframe = None

    @property
    def relevant_data_providers(self) -> List[DataProvider]:
        """Returns the list of the relevant data providers."""
        return self._relevant_data_providers

    @relevant_data_providers.setter
    def relevant_data_providers(self, data_providers: List[DataProvider]) -> None:
        """Takes the update to the lists and converts the DataProviders into their IDs."""
        self._relevant_data_providers = data_providers

        # You have to update the data_frame with the new data providers
        self._create_data_frame()

    @property
    def relevant_data_provider_ids(self) -> List[str]:
        """Returns the string IDs of all relevant DataProviders."""
        return [str(data_provider) for data_provider in self.relevant_data_providers]

    @property
    def data_frame(self) -> pd.DataFrame:
        """Read only access to the underlying dataframe."""
        if self._csv_dataframe is None:
            self._create_data_frame()
        return self._csv_dataframe

    def to_eol_page_id(
        self, identifier: Union[str, int], data_provider: DataProvider = None
    ) -> Optional[Union[List[str], str]]:
        """Returns the corresponding EOL page ID for the given provider ID.
        This method should return None, if no corresponding EOL page ID can be found.
        If the outcome is ambiguous (because the same `identifier` exists in multiple data provider
        namespaces) and no `data_provider` is given for disambiguation, a list of all corresponding
        EOL page IDs is returned.
        """
        return self._access_dataframe_for_id(
            data_provider=data_provider,
            id_provider_column_name=self.CORRESPONDING_ID_ROW_NAME,
            search_value=str(identifier),
            column_to_return=self.EOL_PAGE_ID_ROW_NAME,
        )

    def from_eol_page_id(
        self, eol_page_id: str, data_provider: DataProvider = None
    ) -> Optional[Union[List[str], str]]:
        """Returns the corresponding ID in the provider data for the given EOL page ID.
        This method should return None, if no corresponding ID can be found.
        If the outcome is ambiguous (because there are multiple relevant data providers given that have
        corresponding IDs) and no `data_provider` is given for disambiguation, a list of all corresponding
        IDs is returned.
        """
        return self._access_dataframe_for_id(
            data_provider=data_provider,
            id_provider_column_name=self.EOL_PAGE_ID_ROW_NAME,
            search_value=int(eol_page_id),
            column_to_return=self.CORRESPONDING_ID_ROW_NAME,
        )

    def _create_data_frame(self):
        column_number_of_provider_ids = 2
        column_index = (column_number_of_provider_ids,) * len(
            self.relevant_data_providers
        )
        self._csv_dataframe = read_csv_file(
            self.provider_csv_file_path,
            filter_criteria=tuple(self.relevant_data_provider_ids),
            column_index=column_index,
            dtypes=self.CSV_DTYPES,
        )

    def _access_dataframe_for_id(
        self,
        id_provider_column_name: str,
        search_value: Union[str, int],
        column_to_return: str,
        data_provider: DataProvider = None,
    ) -> Optional[Union[str, List[str]]]:
        df = self.data_frame
        df_corresponding_ids = df.loc[df[id_provider_column_name] == search_value]

        if df_corresponding_ids.empty:
            return None

        if len(df_corresponding_ids) > 1 and data_provider is not None:
            df_corresponding_ids = df_corresponding_ids.loc[
                df_corresponding_ids[self.DATA_PROVIDER_ID_ROW_NAME]
                == int(data_provider)
            ]

        corresponding_ids = df_corresponding_ids.loc[:, column_to_return]
        string_representation = corresponding_ids.to_string(index=False)
        return (
            string_representation
            if len(corresponding_ids) == 1
            else string_representation.split()
        )


def filter_triples_for_predicates(
    triples: Set[Triple], filter_for_predicates: Set[str]
) -> Set[Triple]:
    """Returns a list containing only Triples that have a predicate
    that was given in `filter_for_predicates`.
    If `filter_for_predicates` is None or an empty list, the original list of Triples is returned.
    """
    filtered_triples = triples
    if filter_for_predicates is not None and filter_for_predicates:
        filtered_triples = {
            triple for triple in triples if triple.predicate in filter_for_predicates
        }
    return filtered_triples
