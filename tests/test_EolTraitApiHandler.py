import pytest

from eol.handlers import EolTraitApiHandler


class TestEolTraitApiHandler:
    def test_get_next(self, eol_trait_api_handler):
        cypher_api = eol_trait_api_handler.iterate()
        item1 = next(cypher_api)
        assert isinstance(item1, dict)
        item2 = next(cypher_api)
        assert item2 is not None and len(item2) and item2 != item1

    def test_get_data_from_cypher_api(self, eol_trait_api_handler, cypher_query_string_for_habitat_data):
        response = eol_trait_api_handler.get_data_from_cypher_api(cypher_query_string_for_habitat_data)
        assert len(response) == 5

    @pytest.fixture
    def eol_trait_api_handler(self, eol_api_credentials):
        return EolTraitApiHandler(api_credentials=eol_api_credentials)

    @pytest.fixture
    def cypher_query_string_for_habitat_data(self):
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