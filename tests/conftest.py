import os
import pathlib

import pytest
from dotenv import load_dotenv


@pytest.fixture
def current_directory() -> pathlib.Path:
    return pathlib.Path(__file__).parent


@pytest.fixture
def resource_directory(current_directory) -> pathlib.Path:
    return current_directory / 'data'


@pytest.fixture
def eol_api_credentials(current_directory) -> str:
    load_dotenv()

    token = os.environ['EOL_API_TOKEN']
    return f'JWT {token}'
