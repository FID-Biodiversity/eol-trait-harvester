import pytest

from eol.handlers import EolTraitCsvHandler


class TestEolTraitCsvHandler:
    def test_get_next_returns_dict(self, eol_traits_csv_handler):
        item = next(eol_traits_csv_handler.iterate())
        assert isinstance(item, dict)

    def test_iterate_data_by_key(self, eol_traits_csv_handler):

        data = next(eol_traits_csv_handler.iterate_data_by_key(
            key="page_id", value=45258442
        ))
        assert data["eol_pk"] == "R533-PK221522710"

    @pytest.fixture
    def eol_traits_csv_handler(self, resource_directory):
        csv_file_path_string = resource_directory / "test_eol_traits.csv"
        return EolTraitCsvHandler(csv_file_path_string)
