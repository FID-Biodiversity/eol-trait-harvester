import pytest

from eol.triple_generator import TripleGenerator, Triple


class TestTripleGenerator:
    @pytest.mark.parametrize(
        ["triple_data", "expected_triples"],
        [
            (  # Scenario - Only subject, predicate, object data
                {
                    "literal": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "value_uri": "http://purl.obolibrary.org/obo/ENVO_01000024",
                },
                [
                    Triple(
                        subject="45258442",
                        predicate="http://rs.tdwg.org/dwc/terms/habitat",
                        object="http://purl.obolibrary.org/obo/ENVO_01000024",
                        eol_record_id="R533-PK221522710",
                        source_url=None,
                        citation_text=None,
                    )
                ],
            ),
            (  # Scenario - Only Source given
                {
                    "literal": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "value_uri": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "source": "http://www.marinespecies.org/aphia.php?p=taxdetails&id=227981",
                },
                [
                    Triple(
                        subject="45258442",
                        predicate="http://rs.tdwg.org/dwc/terms/habitat",
                        object="http://purl.obolibrary.org/obo/ENVO_01000024",
                        eol_record_id="R533-PK221522710",
                        source_url="http://www.marinespecies.org/aphia.php?p=taxdetails&id=227981",
                        citation_text=None,
                    )
                ],
            ),
            (  # Scenario - Only Citation given
                {
                    "literal": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "value_uri": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "citation": "Smith, J. (2022): An Amazing Research Paper. Nature",
                },
                [
                    Triple(
                        subject="45258442",
                        predicate="http://rs.tdwg.org/dwc/terms/habitat",
                        object="http://purl.obolibrary.org/obo/ENVO_01000024",
                        eol_record_id="R533-PK221522710",
                        citation_text="Smith, J. (2022): An Amazing Research Paper. Nature",
                        source_url=None,
                    )
                ],
            ),
            (  # Scenario - Both Source and Citation given
                {
                    "literal": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "value_uri": "http://purl.obolibrary.org/obo/ENVO_01000024",
                    "citation": "Smith, J. (2022): An Amazing Research Paper. Nature",
                    "source": "http://www.marinespecies.org/aphia.php?p=taxdetails&id=227981",
                },
                [
                    Triple(
                        subject="45258442",
                        predicate="http://rs.tdwg.org/dwc/terms/habitat",
                        object="http://purl.obolibrary.org/obo/ENVO_01000024",
                        eol_record_id="R533-PK221522710",
                        citation_text="Smith, J. (2022): An Amazing Research Paper. Nature",
                        source_url="http://www.marinespecies.org/aphia.php?p=taxdetails&id=227981",
                    )
                ],
            ),
            (  # Scenario - Unit is given
                {
                    "predicate": "http://purl.obolibrary.org/obo/VT_0001259",
                    "normal_measurement": 9,
                    "units_uri": "http://purl.obolibrary.org/obo/UO_0000021",
                },
                [
                    Triple(
                        subject="45258442",
                        predicate="http://purl.obolibrary.org/obo/VT_0001259",
                        object=9,
                        eol_record_id="R533-PK221522710",
                        unit="http://purl.obolibrary.org/obo/UO_0000021",
                    )
                ],
            ),
        ],
        indirect=["triple_data"],
    )
    def test_create_triples(self, triple_generator, triple_data, expected_triples):
        """Given a single EOL normalized dataset, the correct Triple(s) are generated."""
        triples = triple_generator.create_triples(triple_data)
        assert triples == expected_triples

    @pytest.fixture
    def triple_generator(self):
        return TripleGenerator()

    @pytest.fixture
    def triple_data(self, request):
        eol_data = {
            "eol_record_id": "R533-PK221522710",
            "measurement": None,
            "normal_measurement": None,
            "normal_units": None,
            "object_page_id": None,
            "page_id": 45258442,
            "predicate": "http://rs.tdwg.org/dwc/terms/habitat",
            "resource_id": 459,
            "resource_pk": None,
            "scientific_name": "<i>Adoncholaimus quadriporus</i> Belogurova & Belogurov "
            "1974",
            "units": None,
            "units_uri": None,
        }

        eol_data.update(request.param)
        return eol_data
