from typing import Iterable, Union

import pytest
from eol import EncyclopediaOfLifeProcessing, IdentifierConverterNotSetError
from eol.triple_generator import Triple


class TestEolProcessing:
    """
    General:
        * The process intensive calculations should be done only ONCE! If I call a function of the class the first time,
            I am willing to wait some seconds. However, when I call any other method after that, I want the result
            immediately. Hence, the EOL CSV data should be processed only once - as efficient as possible!
        * The module should provide an enum class that contains the predicates for the currently most relevant traits.
            Hence, I should be able to write code like this:
                filter_by_trait(data, filter_trait=EolTerms.IS_EATEN_BY), where EolTerms.IS_EATEN_BY corresponds to
                "http://purl.obolibrary.org/obo/RO_0002471".
                In case, you don't know Enum classes: https://www.tutorialspoint.com/enum-in-python .
        * Tests should run fast! Hence, I recommend not using the complete EOL dataset,
            but create a small subset (some MB instead of several GB) that represents the original data appropriately
            but will be fast to process! Of course, this test data should be check-in into the repo.
    """

    @pytest.mark.parametrize("eol_page_id", ["1234", "-1"])
    @pytest.mark.parametrize("eol", ["csv", "api"], indirect=True)
    def test_page_id_is_not_valid(self, eol: EncyclopediaOfLifeProcessing, eol_page_id):
        """
        Feature: Function does not throw but returns empty result
            Scenario: The user gives an invalid EOL page ID.
                GIVEN an EOL page ID is invalid or deprecated
                WHEN this EOL page ID is passed to the function
                THEN the function returns an empty result.
        """
        species_traits = eol.get_trait_data_for_eol_page_id(eol_page_id)
        assert len(species_traits) == 0

    @pytest.mark.parametrize(
        ["eol", "expected_trait_count"], [("csv", 7), ("api", 80)], indirect=["eol"]
    )
    def test_non_recursive_data_retrieval(
        self, eol: EncyclopediaOfLifeProcessing, expected_trait_count
    ):
        """
        Feature: Retrieval of taxon trait data from EOL CSV
            Scenario: The user gives a EOL page ID as parameter and wants only the data for the given EOL page ID.
                GIVEN an EOL page ID is given as parameter
                WHEN the EOL page ID is valid
                THEN the function should return a list containing the EOL trait data for only the given EOL page ID.
        """
        species_traits = eol.get_trait_data_for_eol_page_id("311544")
        assert len(species_traits) == expected_trait_count

    @pytest.mark.parametrize(["eol"], [("csv",), ("api",)], indirect=True)
    def test_correct_trait_data_is_retrieved(self, eol: EncyclopediaOfLifeProcessing):
        """
        Feature: The module returns a set of EolData data class objects (https://docs.python.org/3/library/dataclasses.html)
            with the correct data.
            Scenario: The user expects to receive correct data.
                GIVEN a valid EOL page ID is given as parameter
                THEN the function should return a set of EolTrait objects with the correct data.
        """
        eol_page_id = "1143547"
        taxon_trait_data = eol.get_trait_data_for_eol_page_id(eol_page_id)

        assert isinstance(taxon_trait_data, list)
        assert trait_exists(
            eol_page_id,
            "http://purl.obolibrary.org/obo/TO_0000540",
            0.003389,
            taxon_trait_data,
        )
        assert trait_exists(
            eol_page_id,
            "http://eol.org/schema/terms/Present",
            "http://www.geonames.org/6252001",
            taxon_trait_data,
        )
        assert trait_exists(
            eol_page_id,
            "http://eol.org/schema/terms/IntroducedRange",
            "http://www.wikidata.org/entity/Q578170",
            taxon_trait_data,
        )

    @pytest.mark.parametrize(["eol"], [("csv",), ("api",)], indirect=True)
    def test_filtering_of_trait_data(self, eol: EncyclopediaOfLifeProcessing):
        """
        Feature: The module filters the returned trait data by given filters.
            Scenario: The user only wants a subset of the available trait data.
                GIVEN a valid EOL page ID is given as parameter
                    AND a list of filter predicates is given as parameter
                THEN the function should return only a subset of the trait data of the given taxon, containing only
                    data fitting the given filter.
        """
        eol_page_id = "1143547"
        predicate_filters = {
            "http://rs.tdwg.org/dwc/terms/habitat",
            "http://eol.org/schema/terms/Present",
        }
        taxon_trait_data = eol.get_trait_data_for_eol_page_id(
            eol_page_id, filter_for_predicates=predicate_filters
        )

        assert isinstance(taxon_trait_data, list)
        assert len(taxon_trait_data) > 0
        assert all(triple.predicate in predicate_filters for triple in taxon_trait_data)

    @pytest.mark.parametrize(
        ["eol_page_id", "expected_gbif_id"],
        [("21828356", "1057764"), ("52717353", "10577931")],
    )
    def test_get_gbif_id_for_corresponding_eol_id(
        self, eol_with_provider_ids, eol_page_id, expected_gbif_id
    ):
        """
        Feature: The module returns the correct GBIF taxon ID for an EOL page ID.
            Scenario: The user gives an EOL page ID as parameter.
                GIVEN a valid EOL page ID is given as parameter.
                THEN the function should return a string of the corresponding GBIF ID.
        """
        gbif_id = eol_with_provider_ids.get_gbif_id_for_eol_page_id(eol_page_id)
        assert gbif_id == expected_gbif_id

    @pytest.mark.parametrize(
        ["gbif_id", "expected_eol_page_id"],
        [("1057764", "21828356"), ("10577931", "52717353")],
    )
    def test_get_eol_id_for_corresponding_gbif_id(
        self, eol_with_provider_ids, gbif_id, expected_eol_page_id
    ):
        """
        Feature: The module returns the correct EOL page ID for a given GBIF ID.
        """
        eol_page_id = eol_with_provider_ids.get_eol_page_id_from_gbif_id(gbif_id)
        assert eol_page_id == expected_eol_page_id

    def test_corresponding_id_does_not_exist(self, eol_with_provider_ids):
        """
        Feature: If a given EOL page ID has no correspondence in the other data provider,
            return None.
        """
        eol_page_id = eol_with_provider_ids.identifier_converter.from_eol_page_id(
            "46559130"
        )
        assert eol_page_id is None

    def test_identifier_converter_is_called_but_not_set(self, eol):
        """
        Feature: A IdentifierConverterNotSetError is raised, if the an ID conversion is requested
            but no CSV file with the mapping was provided.
        """
        with pytest.raises(IdentifierConverterNotSetError):
            eol.get_gbif_id_for_eol_page_id("46559130")


def trait_exists(
    subject: str, predicate: str, obj: Union[str, float], trait_data: Iterable[Triple]
) -> bool:
    for trait in trait_data:
        if (
            trait.subject == subject
            and trait.predicate == predicate
            and trait.object == obj
        ):
            return True

    return False
