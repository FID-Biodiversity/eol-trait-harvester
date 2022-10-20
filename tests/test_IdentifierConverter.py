import pathlib

import pytest
from eol import IdentifierConverter, DataProvider


class TestIdentifierConverter:
    @pytest.fixture
    def provider_data_csv_file(self):
        current_directory = pathlib.Path(__file__).parent
        return current_directory / 'data/test_provider_ids.csv'

    @pytest.fixture
    def id_converter(self, provider_data_csv_file):
        return IdentifierConverter(provider_csv_file_path=provider_data_csv_file,
                                   relevant_data_providers=[DataProvider.Gbif])

    @pytest.mark.parametrize(['eol_page_id', 'expected_gbif_id'],
                             [('21828356', '1057764'), ('52717353', '10577931')])
    def test_get_gbif_id_for_corresponding_eol_id(self, id_converter, eol_page_id, expected_gbif_id):
        """
        Feature: The module returns the correct GBIF taxon ID for an EOL page ID.
            Scenario: The user gives an EOL page ID as parameter.
                GIVEN a valid EOL page ID is given as parameter.
                THEN the function should return a string of the corresponding GBIF ID.
        """
        gbif_id = id_converter.from_eol_page_id(eol_page_id)
        assert gbif_id == expected_gbif_id

    @pytest.mark.parametrize(['gbif_id', 'expected_eol_page_id'],
                             [('1057764', '21828356'), ('10577931', '52717353')])
    def test_get_eol_id_for_corresponding_gbif_id(self, id_converter, gbif_id, expected_eol_page_id):
        """ Feature: The module returns the correct EOL page ID for a GBIF ID. """
        eol_id = id_converter.to_eol_page_id(gbif_id)
        assert eol_id == expected_eol_page_id

    @pytest.mark.parametrize(['provider_id', 'expected_eol_page_id'],
                             [('1057764', '1234567')])
    def test_identify_ambiguous_id_and_return_only_gbif(self, id_converter, provider_id, expected_eol_page_id):
        """ Feature: The module identifies an ambiguous ID from another data provider and returns
            the correct one.
        """
        id_converter.relevant_data_providers.append(DataProvider.WoRMS)
        multiple_ids = id_converter.to_eol_page_id(provider_id)
        assert isinstance(multiple_ids, list)
        assert len(multiple_ids) == 2

        eol_id = id_converter.to_eol_page_id(provider_id, data_provider=DataProvider.WoRMS)
        assert eol_id == expected_eol_page_id
