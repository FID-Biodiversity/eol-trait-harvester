import json
from copy import copy
from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from eol.handlers import EolTraitApiHandler

from .commons import internet_connection_available


@pytest.mark.skipif(
    not internet_connection_available(), reason="No internet connection available"
)
class TestEolTraitApiHandlerWebCalls:
    def test_get_next(self, eol_trait_api_handler):
        cypher_api = eol_trait_api_handler.iterate()
        item1 = next(cypher_api)
        assert isinstance(item1, dict)
        item2 = next(cypher_api)
        assert item2 is not None and len(item2) and item2 != item1

    def test_get_data_from_cypher_api(
        self, eol_trait_api_handler, cypher_query_string_for_habitat_data
    ):
        response = eol_trait_api_handler.get_data_from_cypher_api(
            cypher_query_string_for_habitat_data
        )
        assert len(response) == 5

    def test_iterate_data_by_key(self, eol_trait_api_handler):
        key_name = "pred.uri"
        value = "http://purl.obolibrary.org/obo/RO_0002303"
        data_generator = eol_trait_api_handler.iterate_data_by_key(
            key=key_name, value=value
        )

        data = next(data_generator)
        assert data[key_name] == value


class TestEolTraitApiHandlerUnittests:
    def test_paginate_cypher_api(self, eol_trait_api_handler):
        eol_trait_api_handler.read_api_with_parameters = Mock()
        eol_trait_api_handler.read_api_with_parameters.side_effect = (
            generate_mock_responses(number_of_responses=3)
        )

        list(
            eol_trait_api_handler.paginate_cypher_api(
                "MATCH (trait:Trait) RETURN trait LIMIT 100;"
            )
        )

        expected_queries = [
            eol_trait_api_handler.compose_cypher_url(
                "MATCH (trait:Trait) RETURN trait SKIP 0 LIMIT 100"
            ),
            eol_trait_api_handler.compose_cypher_url(
                "MATCH (trait:Trait) RETURN trait SKIP 100 LIMIT 100"
            ),
            eol_trait_api_handler.compose_cypher_url(
                "MATCH (trait:Trait) RETURN trait SKIP 200 LIMIT 100"
            ),
        ]

        for query in expected_queries:
            eol_trait_api_handler.read_api_with_parameters.assert_any_call(query)


@pytest.fixture(scope="module")
def eol_trait_api_handler(eol_api_credentials):
    return EolTraitApiHandler(api_credentials=eol_api_credentials)


@pytest.fixture
def cypher_query_string_for_habitat_data():
    return """MATCH (t:Trait)<-[:trait]-(p:Page),
        (t)-[:supplier]->(r:Resource),
        (t)-[:predicate]->(pred:Term)
        WHERE pred.uri = "http://purl.obolibrary.org/obo/RO_0002303"
        OPTIONAL MATCH (t)-[:object_term]->(obj:Term)
        OPTIONAL MATCH (t)-[:normal_units_term]->(units:Term)
        RETURN r.resource_id, t.eol_pk, t.resource_ok, t.source,
        p.page_id, t.scientific_name, pred.uri, pred.name,
        t.object_page_id, obj.uri, obj.name, t.normal_measurement,
        units.uri, units.name, t.normal_units, t.literal
        LIMIT 5"""


@dataclass
class MockResponse:
    status_code: int
    text: str


def generate_mock_responses(number_of_responses=100):
    mock_data = {
        "columns": ["p.page_id", "t.scientific_name"],
        "data": [(12345, "Fagus testus")],
    }

    last_element = copy(mock_data)
    last_element["data"] = []

    responses = [
        MockResponse(text=json.dumps(mock_data), status_code=200)
        for _ in range(0, number_of_responses)
    ]

    responses[-1] = MockResponse(text=json.dumps(last_element), status_code=200)

    return responses
