import pathlib
from enum import Enum
from functools import partial
from io import StringIO
from typing import Generator, List, Tuple, Union

import pandas as pd


class DataProvider(Enum):
    """A simple interface for accessing data provider IDs.
    Entities generated from https://opendata.eol.org/dataset/identifier-map
    Their representation always returns its value (i.e. the provider ID).
    """

    Frost = "726"  # Frost's 2018 Amphibian Species of the World
    Gbif = "767"  # GBIF
    ITIS = "695"  # Integrated Taxonomic Information System (ITIS)
    IUCN = "5"  # IUCN
    NCBI = "676"  # National Center for Biotechnology Information (NCBI)
    WoRMS = "459"  # World Register of Marine Species (WoRMS)

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.__repr__()

    def __int__(self):
        return int(self.value)


def read_csv_file(
    csv_file_path: Union[pathlib.Path, str],
    filter_criteria: Tuple[Union[str, int]] = None,
    column_index: Tuple[int] = None,
    delimiter: str = ",",
    dtypes: dict = None,
) -> pd.DataFrame:
    """Reads an arbitrary large CSV file, filters the data while reading and returns
    the corresponding DataFrame.

    `filter_criteria` and `column_index` have to be either None or have to have
    the same length! If neither is the case, a ValueError will be thrown!
    """
    with open(csv_file_path, "r") as in_file:
        column_names = next(in_file)  # The first line should be the column names
        data_frame = generate_dataframe_from_stream(
            in_file,
            filter_criteria=filter_criteria,
            column_index=column_index,
            delimiter=delimiter,
            dtypes=dtypes,
            column_names=column_names.split(delimiter),
        )
        return data_frame


def generate_dataframe_from_stream(
    stream,
    filter_criteria: Tuple[Union[str, int]],
    column_index: Tuple[int],
    delimiter: str = ",",
    dtypes: dict = None,
    column_names: List[str] = None,
) -> pd.DataFrame:
    """Takes an open file stream from a CSV file and converts a DataFrame from it.
    `filter_criteria` and `column_index` have to be both None or have to have the
    same length! If either is not the case, a ValueError will be thrown!
    """
    if filter_criteria is not None and len(filter_criteria) != len(column_index):
        raise ValueError(
            "filter_criteria and column_index do not have the same length!"
        )

    stream_generator = (
        _iterate_lines
        if filter_criteria is None
        else partial(
            _filter_stream, filter_criteria=filter_criteria, column_index=column_index
        )
    )

    filtered_csv_content = "".join(stream_generator(stream, delimiter=delimiter))
    df = pd.read_csv(
        filepath_or_buffer=StringIO(filtered_csv_content),
        names=column_names,
        dtype=dtypes,
    )

    return df


def _filter_stream(
    stream,
    filter_criteria: Tuple[Union[str, int]],
    column_index: Tuple[int],
    delimiter: str = ",",
) -> Generator[list, None, None]:
    yield from (
        delimiter.join(split_line_data)
        for split_line_data in _iterate_lines(stream, delimiter, split_line=True)
        for n, index in enumerate(column_index, start=0)
        if filter_criteria[n] == split_line_data[index]
    )


def _iterate_lines(
    file_io, delimiter: str, split_line: bool = False
) -> Generator[Union[str, list], None, None]:
    for line in file_io:
        yield line.split(delimiter) if split_line else line
