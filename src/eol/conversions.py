from __future__ import annotations

import logging
import pathlib
from typing import List, Optional, Union

import pandas as pd

from eol.data import DataProvider, read_csv_file


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
    RELEVANT_COLUMNS = [
        CORRESPONDING_ID_ROW_NAME,
        EOL_PAGE_ID_ROW_NAME,
        DATA_PROVIDER_ID_ROW_NAME,
    ]

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

        self.logger = logging.getLogger(__name__)

    @property
    def relevant_data_providers(self) -> List[DataProvider]:
        """Returns the list of the relevant data providers."""
        return self._relevant_data_providers

    @relevant_data_providers.setter
    def relevant_data_providers(self, data_providers: List[DataProvider]) -> None:
        """Takes the update to the lists and converts the DataProviders into their
        IDs.
        """
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
        self,
        identifier: Union[str, int, list[Union[str, int]]],
        data_provider: DataProvider = None,
    ) -> Optional[Union[List[str], str]]:
        """Returns the corresponding EOL page ID for the given provider ID.

        This method should return None, if no corresponding EOL page ID can be found.
        If the outcome is ambiguous (because the same `identifier` exists in multiple
        data provider namespaces) and no `data_provider` is given for disambiguation,
        a list of all corresponding EOL page IDs is returned.

        If provided a list of identifiers, a corresponding list with EOL page IDs is
        returned. The returned list will have the same order as the given identifiers.
        If no corresponding EOL page ID could be retrieved, the corresponding value
        will be None.
        """
        return self._access_dataframe_for_id(
            data_provider=data_provider,
            id_provider_column_name=self.CORRESPONDING_ID_ROW_NAME,
            search_value=identifier,
            column_to_return=self.EOL_PAGE_ID_ROW_NAME,
        )

    def from_eol_page_id(
        self, eol_page_id: str, data_provider: DataProvider = None
    ) -> Optional[Union[List[str], str]]:
        """Returns the corresponding ID in the provider data for the given EOL page ID.
        This method should return None, if no corresponding ID can be found.
        If the outcome is ambiguous (because there are multiple relevant data providers
        given that have corresponding IDs) and no `data_provider` is given for
        disambiguation, a list of all corresponding IDs is returned.
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
        self.logger.info("Reading EOL data provider mapping...")
        self._csv_dataframe = read_csv_file(
            self.provider_csv_file_path,
            filter_criteria=tuple(self.relevant_data_provider_ids),
            column_index=column_index,
            dtypes=self.CSV_DTYPES,
        )
        self.logger.info("Done!")

    def _access_dataframe_for_id(
        self,
        id_provider_column_name: str,
        search_value: Union[str, int, list[Union[str, int]]],
        column_to_return: str,
        data_provider: DataProvider = None,
    ) -> Optional[Union[str, List[str]]]:
        if isinstance(search_value, (str, int)):
            result = self._process_single_value(
                search_value,
                self.data_frame,
                id_provider_column_name,
                column_to_return,
                data_provider,
            )
        else:
            result = self._process_list(
                search_value, self.data_frame, id_provider_column_name, column_to_return
            )

        return result

    def _process_single_value(
        self,
        value: Union[str, int],
        df: pd.DataFrame,
        id_provider_column_name: str,
        column_to_return: str,
        data_provider: Optional[DataProvider] = None,
    ) -> str:
        df_corresponding_ids = df.loc[df[id_provider_column_name] == value]

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

    def _process_list(
        self,
        values: list[Union[str, int]],
        df: pd.DataFrame,
        id_provider_column_name: str,
        column_to_return: str,
    ) -> list[str]:
        df_for_search_values = df.loc[df.isin(values)[id_provider_column_name]]

        search_value_look_up = {
            row[id_provider_column_name]: str(row[column_to_return])
            for _, row in df_for_search_values.iterrows()
        }

        return [search_value_look_up.get(v) for v in values]
