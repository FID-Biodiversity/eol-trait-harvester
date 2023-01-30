import json
import pathlib
import re
from typing import Any, Generator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import requests


class DataHandler:
    """An interface class for all EOL sources.
    All Handler classes should obey this schema, although not inherit from it.
    """

    def iterate(self) -> Generator[dict, None, None]:

        """Returns a generator yielding the items in the data source."""
        ...

    def iterate_data_by_key(
        self, key: str, value: Optional[Any] = None
    ) -> Generator[dict, None, None]:
        """Iterate all data for the given key.
        If a `value` is given, only data having this value will be returned.
        If the key and/or the value cannot be found, an empty DataFrame is returned.
        """


class EolTraitCsvHandler:
    """Takes care of reading and converting data from a EOL traits CSV file.
    This is a DataHandler class and obeys the DataHandler interface.
    """

    # Data loading is restricted to specific columns
    # Remove unused column names to save memory
    required_columns = [
        "eol_pk",
        "page_id",
        "resource_pk",
        "resource_id",
        "source",
        "scientific_name",
        "predicate",
        "object_page_id",
        "value_uri",
        "normal_measurement",
        "normal_units_uri",
        "normal_units",
        "measurement",
        "units_uri",
        "units",
        "literal",
    ]

    column_types = {"page_id": "int64", "resource_id": "int16"}

    def __init__(self, csv_file_path: Union[pathlib.Path, str]):
        if not isinstance(csv_file_path, pathlib.Path):
            csv_file_path = pathlib.Path(csv_file_path)

        self.csv_file_path = csv_file_path
        self._data: Optional[pd.DataFrame] = None

    def iterate(self) -> Generator[dict, None, None]:
        """Returns a generator yielding the items in the data source."""
        for index, csv_row_data in self.get_data().iterrows():
            yield convert_pandas_object_to_dict(csv_row_data)

    def iterate_data_by_key(self, key: str, value: Any) -> Generator[dict, None, None]:
        """Iterate all data for the given key, which also has to have the given `value`.
        If the key and/or the value cannot be found, an empty DataFrame is returned.
        """
        df = self.get_data()
        data = df.loc[df[key] == value]

        for index, series in data.iterrows():
            yield convert_pandas_object_to_dict(series)

    def get_data(self) -> pd.DataFrame:
        """Get the complete dataset available."""
        if self._data is None:
            self._data = self._create_data()
        return self._data

    def _create_data(self) -> pd.DataFrame:
        data = pd.read_csv(
            self.csv_file_path, usecols=self.required_columns, dtype=self.column_types
        )
        # Replace all NaN values with None
        data = data.replace({np.nan: None})

        return data


class EolTraitApiHandler:
    """Takes care of reading and converting data from the EOL Cypher Web-API.
    This is a DataHandler class and obeys the DataHandler interface.

    "columns": [
            "r.resource_id",
            "t.eol_pk",
            "t.resource_ok",
            "t.source",
            "p.page_id",
            "t.scientific_name",
            "pred.uri",
            "pred.name",
            "t.object_page_id",
            "obj.uri",
            "obj.name",
            "t.normal_measurement",
            "units.uri",
            "units.name",
            "t.normal_units",
            "t.literal"
    ]
    """

    parameter_name_normalizations = {"page_id": "p.page_id"}

    def __init__(self, api_credentials):
        self.api_credentials = api_credentials
        self.session = create_http_session(api_credentials)

    def iterate(self) -> Generator[dict, None, None]:
        """Returns a generator yielding the items in the data source."""
        iterate_everything_query_string = "MATCH (trait:Trait) RETURN trait LIMIT 100;"
        return self.iterate_cypher_response_for_query(iterate_everything_query_string)

    def iterate_data_by_key(
        self, key: str, value: Optional[Any] = None
    ) -> Generator[dict, None, None]:
        """Iterate all data for the given key.
        If a `value` is given, only data having this value will be returned.
        If the key and/or the value cannot be found, an empty DataFrame is returned.
        """
        key = self.normalize_key_parameter(key)

        filtered_iteration_string = self.convert_key_value_pairs_to_cypher_query(
            keys=[key], values=[value]
        )
        return self.iterate_cypher_response_for_query(filtered_iteration_string)

    def iterate_cypher_response_for_query(
        self, cypher_query_string: str
    ) -> Generator[dict, None, None]:
        for response in self.paginate_cypher_api(cypher_query_string):
            self.raise_if_response_contains_error(response)

            for data in self.convert_cypher_response_data_to_list(response.text):
                yield data

    def normalize_key_parameter(self, parameter_name: str) -> str:
        return self.parameter_name_normalizations.get(parameter_name, parameter_name)

    def get_data_from_cypher_api(self, cypher_query_string: str) -> List[dict]:
        """Calls the EOL Cypher API and returns the response as dict.
        Raises an SyntaxError, if the Cypher API returns an error.
        """
        url = self.compose_cypher_url(cypher_query_string)
        response = self.read_api_with_parameters(url)

        self.raise_if_response_contains_error(response)

        return self.convert_cypher_response_data_to_list(response.text)

    def paginate_cypher_api(self, cypher_query_string: str, **kwargs) -> Generator:
        """Yields successively the responses of a paging of the EOL Cypher API."""
        number_of_returned_entries = 0

        if "limit" not in cypher_query_string.lower():
            raise ValueError("You have to provide a LIMIT to your query!")

        # Remove trailing semicolons
        if cypher_query_string.endswith(";"):
            cypher_query_string = cypher_query_string[:-1]

        limit_count, limit_string = self.extract_limit_count_and_string(
            cypher_query_string
        )
        limit_count = int(limit_count)

        # Remove limit count, it has to come after (!) the SKIP
        cypher_query_string = cypher_query_string.replace(limit_string, "")

        url = self.compose_cypher_url(cypher_query_string)

        while True:
            skip_string = f"SKIP {number_of_returned_entries} {limit_string}"
            ready_url = f"{url} {skip_string}"

            cypher_response = self.read_api_with_parameters(ready_url, **kwargs)

            if self._is_data_response_empty(cypher_response):
                return
            else:
                yield cypher_response

            number_of_returned_entries += limit_count

    def read_api_with_parameters(self, url: str, **kwargs):
        return self.session.post(url, params=kwargs)

    def compose_cypher_url(self, cypher_query: str) -> str:
        return f"https://eol.org/service/cypher?query={cypher_query.strip()}"

    def _is_data_response_empty(self, cypher_response) -> bool:
        empty_data_indication_string = '"data":[]'
        return empty_data_indication_string in cypher_response.text.replace(": ", ":")

    def extract_limit_count_and_string(self, query_string: str) -> Tuple[str, str]:
        """Returns the limit count and the complete limit string, in this order."""
        regex_limit_count = re.search("(LIMIT ([0-9]+))", query_string, re.IGNORECASE)
        return regex_limit_count.group(2), regex_limit_count.group(1)

    def raise_if_response_contains_error(self, response):
        if response.status_code != 200:
            raise SyntaxError(
                f"The EOL API returned with an error! Message: {response}"
            )

    def convert_cypher_response_data_to_list(self, response_data: str) -> List[dict]:
        data_json = json.loads(response_data)
        column_names = data_json["columns"]
        return [
            {name: value for name, value in zip(column_names, element)}
            for element in data_json["data"]
        ]

    def convert_key_value_pairs_to_cypher_query(
        self, keys: List[str], values: List[str], query_limit: int = 100
    ) -> str:
        values = [f'"{v}"' if str(v).startswith("http") else v for v in values]

        # The ORDER BY command is mandatory to make pagination predictable.
        # In Neo4J, the return order may (!) be continuous, but it seems to
        # depend on the data.
        order_by_variable = "t.eol_pk"
        return_variables = [
            "obj.name",
            "obj.uri",
            "p.citation",
            "p.page_id",
            "pred.name",
            "pred.uri",
            "r.resource_id",
            "t.citation",
            "t.eol_pk",
            "t.literal",
            "t.normal_measurement",
            "t.normal_units",
            "t.object_page_id",
            "t.resource_ok",
            "t.scientific_name",
            "t.source",
            "units.name",
            "units.uri",
        ]

        return f"""MATCH (t:Trait)<-[:trait]-(p:Page),
    (t)-[:supplier]->(r:Resource),
    (t)-[:predicate]->(pred:Term)
    WHERE {' AND '.join(f'{key} = {value}' for key, value in zip(keys, values))}
    OPTIONAL MATCH (t)-[:object_term]->(obj:Term)
    OPTIONAL MATCH (t)-[:normal_units_term]->(units:Term)
    RETURN {', '.join(return_variables)}
    ORDER BY {order_by_variable}
    LIMIT {query_limit}"""


def create_http_session(credentials=None, headers: dict = None) -> requests.Session:
    """Establishes a reusable HTTP session."""
    session = requests.Session()

    if credentials is not None:
        session.headers["Authorization"] = credentials

    if headers is not None:
        session.headers.update(headers)

    return session


def extract_limit_count_and_string(query_string: str) -> Tuple[str, str]:
    """Returns the limit count and the complete limit string, in this order."""
    regex_limit_count = re.search("(LIMIT ([0-9]+))", query_string, re.IGNORECASE)
    return regex_limit_count.group(2), regex_limit_count.group(1)


def raise_if_response_contains_error(response):
    if response.status_code != 200:  # http code for recheck
        raise SyntaxError(f"The EOL API returned with an error! Message: {response}")


def convert_pandas_object_to_dict(pandas_obj) -> dict:
    if isinstance(pandas_obj, pd.Series):
        new_dict = dict(pandas_obj.to_dict())
    else:
        new_dict = dict(pandas_obj.to_dict(orient="index"))
        keys = list(new_dict.keys())
        new_dict = new_dict[keys[0]]

    return new_dict


if __name__ == "__main__":
    from pprint import pprint

    eol = EolTraitCsvHandler("../../tests/data/test_eol_traits.csv")
    data = next(eol.iterate_data_by_key(key="page_id", value=45258442))
    pprint(data)
