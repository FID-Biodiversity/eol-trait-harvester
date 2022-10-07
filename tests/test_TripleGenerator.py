import pytest

from eol.triple_generator import TripleGenerator, Triple


class TestTripleGenerator:
    @pytest.mark.parametrize(
        ["triple_data", "expected_triples"],
        [
            (
                {
                    "eol_pk": "R533-PK221522710",
                    "literal": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "measurement": None,
                    "normal_measurement": None,
                    "normal_units": None,
                    "object_page_id": None,
                    "pageID": 45258442,
                    "predicate": "http://rs.tdwg.org/dwc/terms/habitat",
                    "resource_id": 459,
                    "resource_pk": None,
                    "scientific_name": "<i>Adoncholaimus quadriporus</i> Belogurova & Belogurov "
                    "1974",
                    "source": "http://www.marinespecies.org/aphia.php?p=taxdetails&id=227981",
                    "units": None,
                    "units_uri": None,
                    "value_uri": "http://purl.obolibrary.org/obo/ENVO_01000024",
                },
                [
                    Triple(
                        subject='45258442',
                        predicate="http://rs.tdwg.org/dwc/terms/habitat",
                        object="http://purl.obolibrary.org/obo/ENVO_01000024",
                    )
                ],
            )
        ],
    )
    def test_create_triples(self, triple_generator, triple_data, expected_triples):
        triples = triple_generator.create_triples(triple_data)
        assert triples == expected_triples

    @pytest.fixture
    def triple_generator(self):
        return TripleGenerator()
