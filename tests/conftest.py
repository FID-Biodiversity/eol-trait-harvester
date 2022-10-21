import os
import pathlib
from typing import Optional

import pytest
from dotenv import load_dotenv

from eol import EncyclopediaOfLifeProcessing
from eol.handlers import EolTraitCsvHandler, EolTraitApiHandler
from eol.normalization import EolTraitCsvNormalizer, EolTraitApiNormalizer


@pytest.fixture(scope="session")
def current_directory() -> pathlib.Path:
    return pathlib.Path(__file__).parent


@pytest.fixture(scope="session")
def resource_directory(current_directory) -> pathlib.Path:
    return current_directory / "data"


@pytest.fixture(scope="session")
def provider_ids_csv_file_path(resource_directory) -> pathlib.Path:
    return resource_directory / "test_provider_ids.csv"


@pytest.fixture(scope="session")
def eol_api_credentials(current_directory) -> Optional[str]:
    load_dotenv()

    token = os.environ.get("EOL_API_TOKEN")
    return f"JWT {token}" if token is not None else None


@pytest.fixture
def eol_trait_csv_file_path() -> str:
    current_directory = pathlib.Path(__file__).parent
    return str(pathlib.Path(current_directory, "data/test_eol_traits.csv").absolute())


@pytest.fixture
def eol_with_csv_handler(
    eol_trait_csv_file_path, provider_ids_csv_file_path
) -> EncyclopediaOfLifeProcessing:
    handler = EolTraitCsvHandler(eol_trait_csv_file_path)
    normalizer = EolTraitCsvNormalizer()

    return EncyclopediaOfLifeProcessing(handler, normalizer, provider_ids_csv_file_path)


@pytest.fixture
def eol_with_api_handler(
    eol_api_credentials, provider_ids_csv_file_path
) -> EncyclopediaOfLifeProcessing:
    handler = EolTraitApiHandler(eol_api_credentials)
    normalizer = EolTraitApiNormalizer()

    return EncyclopediaOfLifeProcessing(handler, normalizer, provider_ids_csv_file_path)


@pytest.fixture
def eol(request, eol_with_api_handler, eol_with_csv_handler):
    try:
        if request.param == "csv":
            return eol_with_csv_handler
        elif request.param == "api":
            return eol_with_api_handler
    except AttributeError:
        # CSV trait handler is default
        return eol_with_csv_handler
