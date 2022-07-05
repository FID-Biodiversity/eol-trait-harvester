import json
import pathlib
import re
from typing import Generator, Union, Optional, Any, Tuple, List

import pandas as pd
import requests


class DataHandler:
    """ An interface class for all EOL sources.
        All Handler classes should obey this schema, although not inherit from it.
    """
    def iterate(self) -> Generator[dict, None, None]:
        """ Returns a generator yielding normalized view of the items in the data source. """
        ...

    def get_data_filtered_by_value(self, key: str, value: Any) -> dict:
        """ Get the dataset available, but filtered the value of the given key.
            If the key and/or the value cannot be found, an empty DataFrame is returned.
        """


class EolTraitCsvHandler:
    """ Takes care of reading and converting data from a EOL traits CSV file.
        This is a DataHandler class and obeys the DataHandler interface.
    """

    # Data loading is restricted to specific columns
    # Remove unused column names to save memory
    required_columns = ['eol_pk',
                        'page_id',
                        'resource_pk',
                        'resource_id',
                        'source',
                        'scientific_name',
                        'predicate',
                        'object_page_id',
                        'value_uri',
                        'normal_measurement',
                        'normal_units_uri',
                        'normal_units',
                        'measurement',
                        'units_uri',
                        'units',
                        'literal']

    column_types = {
        'page_id': 'int64',
        'resource_id': 'int16',
        'value_uri': 'category',
        'predicate': 'category'
    }

    def __init__(self, csv_file_path: Union[pathlib.Path, str]):
        if not isinstance(csv_file_path, pathlib.Path):
            csv_file_path = pathlib.Path(csv_file_path)

        self.csv_file_path = csv_file_path
        self._data: Optional[pd.DataFrame] = None

    def iterate(self) -> Generator[dict, None, None]:
        """ Returns a generator yielding normalized view of the items in the data source. """
        for index, csv_row_data in self.get_data().iterrows():
            yield convert_pandas_object_to_dict(csv_row_data)

    def get_data_filtered_by_value(self, key: str, value: Any) -> dict:
        """ Get the dataset available, but filtered the value of the given key.
            If the key and/or the value cannot be found, an empty DataFrame is returned.
        """
        df = self.get_data()
        data = df.loc[df[key] == value]
        return convert_pandas_object_to_dict(data)

    def get_data(self) -> pd.DataFrame:
        """ Get the complete dataset available. """
        if self._data is None:
            self._data = self._create_data()
        return self._data

    def _create_data(self) -> pd.DataFrame:
        return pd.read_csv(self.csv_file_path, usecols=self.required_columns, dtype=self.column_types)


class EolTraitApiHandler:
    """ Takes care of reading and converting data from the EOL Cypher Web-API.
        This is a DataHandler class and obeys the DataHandler interface.
    """

    def __init__(self, api_credentials):
        self.api_credentials = api_credentials
        self.session = create_http_session(api_credentials)

    def iterate(self) -> Generator[dict, None, None]:
        """ Returns a generator yielding normalized view of the items in the data source. """
        iterate_everything_query_string = 'MATCH (trait:Trait) RETURN trait LIMIT 100;'
        for response in self.paginate_cypher_api(iterate_everything_query_string):
            raise_if_response_contains_error(response)

            for data in convert_cypher_response_data_to_list(response.text):
                yield data

    def get_data_filtered_by_value(self, key: str, value: Any) -> dict:
        """ Get the dataset available, but filtered the value of the given key.
            If the key and/or the value cannot be found, an empty DataFrame is returned.
        """
        pass

    def get_data_from_cypher_api(self, cypher_query_string: str) -> List[dict]:
        """ Calls the EOL Cypher API and returns the response as dict.
            Raises an SyntaxError, if the Cypher API returns an error.
        """
        url = self._compose_cypher_url(cypher_query_string)
        response = self.read_api_with_parameters(url)

        raise_if_response_contains_error(response)

        return convert_cypher_response_data_to_list(response.text)

    def paginate_cypher_api(self, cypher_query_string: str, **kwargs) -> Generator:
        """ Yields successively the responses of a paging of the EOL Cypher API. """
        number_of_returned_entries = 0

        if 'limit' not in cypher_query_string.lower():
            raise ValueError('You have to provide a LIMIT to your query!')

        # Remove trailing semicolons
        if cypher_query_string.endswith(';'):
            cypher_query_string = cypher_query_string[:-1]

        limit_count, limit_string = extract_limit_count_and_string(cypher_query_string)

        # Remove limit count, it has to come after (!) the SKIP
        cypher_query_string = cypher_query_string.replace(limit_string, '')

        url = self._compose_cypher_url(cypher_query_string)

        while True:
            skip_string = f'SKIP {number_of_returned_entries} {limit_string}'
            url = f'{url} {skip_string}'

            yield self.read_api_with_parameters(url, **kwargs)

            number_of_returned_entries += limit_count

    def read_api_with_parameters(self, url: str, **kwargs):
        return self.session.get(url, params=kwargs)

    def _compose_cypher_url(self, cypher_query: str) -> str:
        return f'https://eol.org/service/cypher?query={cypher_query}'


def create_http_session(credentials=None, headers: dict = None) -> requests.Session:
    """ Establishes a reusable HTTP session. """
    session = requests.Session()

    if credentials is not None:
        session.headers['Authorization'] = credentials

    if headers is not None:
        session.headers.update(headers)

    return session


def extract_limit_count_and_string(query_string: str) -> Tuple[str, str]:
    """ Returns the limit count and the complete limit string, in this order. """
    regex_limit_count = re.search('(LIMIT ([0-9]+))', query_string, re.IGNORECASE)
    return regex_limit_count.group(2), regex_limit_count.group(1)


def raise_if_response_contains_error(response):
    if response.status_code != 200:
        raise SyntaxError(f'The EOL API returned with an error! Message: {response}')


def convert_pandas_object_to_dict(pandas_obj) -> dict:
    if isinstance(pandas_obj, pd.Series):
        new_dict = dict(pandas_obj.to_dict())
    else:
        new_dict = dict(pandas_obj.to_dict(orient='index'))
        keys = list(new_dict.keys())
        new_dict = new_dict[keys[0]]

    return new_dict


def convert_cypher_response_data_to_list(response_data: str) -> List[dict]:
    data_json = json.loads(response_data)
    column_names = data_json['columns']
    return [{name: value for name, value in zip(column_names, element)}
            for element in data_json['data']
            ]


if __name__ == '__main__':
    from pprint import pprint
    eol = EolTraitCsvHandler('../tests/data/test_eol_traits.csv')
    data = eol.get_data_filtered_by_value(key='page_id', value=45258442)
    pprint(data)
