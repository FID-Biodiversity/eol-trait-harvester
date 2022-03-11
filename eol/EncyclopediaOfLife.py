# -*- coding: utf-8 -*-

"""
Harvest data from Encyclopedia of Life (https://eol.org/)
"""
__author__ = "Ischa Tahir"
__copyright__ = "(c) Senckenberg Gesellschaft für Naturforschung 2022"

import pathlib
from enum import Enum
from typing import Optional, Union, List

import pandas as pd

from eol.data import read_csv_file, Triple


class EncyclopediaOfLifeProcessing:
    """ This class orchestrates the data calls to the Encyclopedia of Life. """
    def __init__(self, identifier_converter):
        self.identifier_converter = None

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


class DataProvider(Enum):
    """ A simple interface for accessing data provider IDs.
        Entities generated from https://opendata.eol.org/dataset/identifier-map
        Their representation always returns its value (i.e. the provider ID).
    """
    Frost = '726'   # Frost's 2018 Amphibian Species of the World
    Gbif = '767'    # GBIF
    ITIS = '695'    # Integrated Taxonomic Information System (ITIS)
    IUCN = '5'      # IUCN
    NCBI = '676'    # National Center for Biotechnology Information (NCBI)
    WoRMS = '459'   # World Register of Marine Species (WoRMS)

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.__repr__()

    def __int__(self):
        return int(self.value)


class IdentifierConverter:
    """ A class for converting any provider ID into an EOL page ID. """

    CORRESPONDING_ID_ROW_NAME = 'resource_pk'
    EOL_PAGE_ID_ROW_NAME = 'page_id'
    DATA_PROVIDER_ID_ROW_NAME = 'resource_id'
    CSV_DTYPES = {
        DATA_PROVIDER_ID_ROW_NAME: 'int',
        CORRESPONDING_ID_ROW_NAME: 'str',
        EOL_PAGE_ID_ROW_NAME: 'int'}

    def __init__(self, provider_csv_file_path: Union[str, pathlib.Path],
                 relevant_data_providers: Union[List[DataProvider], DataProvider] = None):

        self.provider_csv_file_path = pathlib.Path(provider_csv_file_path) \
            if isinstance(provider_csv_file_path, str) else provider_csv_file_path

        relevant_data_providers = [relevant_data_providers] \
            if isinstance(relevant_data_providers, DataProvider) else relevant_data_providers
        self._relevant_data_providers = [str(provider) for provider in relevant_data_providers]

        self._csv_dataframe = None

    @property
    def relevant_data_providers(self) -> List[str]:
        """ Returns a copy (!) of the list with the IDs of the relevant data providers.
            To modify this list, you have to explicitly set it!
        """
        return [str(data_provider) for data_provider in self._relevant_data_providers]

    @relevant_data_providers.setter
    def relevant_data_providers(self, data_providers: list) -> None:
        """ Takes the update to the lists and converts the DataProviders into their IDs. """
        self._relevant_data_providers = [str(data_provider) for data_provider in data_providers]

        # You have to update the data_frame with the new data providers
        self._create_data_frame()

    @property
    def data_frame(self) -> pd.DataFrame:
        """ Read only access to the underlying dataframe. """
        if self._csv_dataframe is None:
            self._create_data_frame()
        return self._csv_dataframe

    def to_eol_page_id(self, identifier: Union[str, int], data_provider: DataProvider = None) -> str:
        """ Returns the corresponding EOL page ID for the given provider ID.
            This method should return None, if no corresponding EOL page ID can be found.
        """
        return self._access_dataframe_for_id(data_provider=data_provider,
                                             id_provider_column_name=self.CORRESPONDING_ID_ROW_NAME,
                                             search_value=str(identifier),
                                             column_to_return=self.EOL_PAGE_ID_ROW_NAME)

    def from_eol_page_id(self, eol_page_id: str, data_provider: DataProvider = None) -> Optional[str]:
        """ Returns the corresponding ID in the provider data for the given EOL page ID.
            This method should return None, if no corresponding ID can be found.
        """
        return self._access_dataframe_for_id(data_provider=data_provider,
                                             id_provider_column_name=self.EOL_PAGE_ID_ROW_NAME,
                                             search_value=int(eol_page_id),
                                             column_to_return=self.CORRESPONDING_ID_ROW_NAME)

    def _create_data_frame(self):
        column_number_of_provider_ids = 2
        column_index = (column_number_of_provider_ids,) * len(self.relevant_data_providers)
        self._csv_dataframe = read_csv_file(self.provider_csv_file_path,
                                            filter_criteria=tuple(self.relevant_data_providers),
                                            column_index=column_index,
                                            dtypes=self.CSV_DTYPES)

    def _access_dataframe_for_id(self, id_provider_column_name: str, search_value: Union[str, int],
                                 column_to_return: str, data_provider: DataProvider = None) -> Optional[Union[str, List[str]]]:
        df = self.data_frame
        df_corresponding_ids = df.loc[df[id_provider_column_name] == search_value]

        if df_corresponding_ids.empty:
            return None

        if len(df_corresponding_ids) > 1 and data_provider is not None:
            df_corresponding_ids = df_corresponding_ids.loc[df_corresponding_ids[
                                                         self.DATA_PROVIDER_ID_ROW_NAME] == int(data_provider)]

        corresponding_ids = df_corresponding_ids.loc[:, column_to_return]
        string_representation = corresponding_ids.to_string(index=False)
        return string_representation if len(corresponding_ids) == 1 else string_representation.split()
