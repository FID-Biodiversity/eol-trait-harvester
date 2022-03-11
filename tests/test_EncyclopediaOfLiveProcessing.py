import pathlib
from typing import Iterable

import pytest

from coding.eol_provider_mapping.gbif_eol_mapping import EncyclopediaOfLifeProcessing, Triple


@pytest.fixture
def path_to_unzipped_eol_csv_files() -> str:
    current_directory = pathlib.Path(__file__).parent
    return str(pathlib.Path(current_directory, 'data/test_provider_ids.csv').absolute())


@pytest.fixture
def eol(path_to_unzipped_eol_csv_files) -> EncyclopediaOfLifeProcessing:
    eol = EncyclopediaOfLifeProcessing()
    eol.csv_path = path_to_unzipped_eol_csv_files
    return eol


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

    @pytest.mark.parametrize('eol_page_id', ['1234', '-1'])
    def test_page_id_is_not_valid(self, eol, eol_page_id):
        """
        Feature: Function does not throw but returns empty result
            Scenario: The user gives an invalid EOL page ID.
                GIVEN an EOL page ID is invalid or deprecated
                WHEN this EOL page ID is passed to the function
                THEN the function returns an empty result.
        """
        species_traits = eol.get_trait_data_for_eol_page_id(eol_page_id)
        assert len(species_traits) == 0

    def test_non_recursive_data_retrieval(self, eol):
        """
        Feature: Retrieval of taxon trait data from EOL CSV
            Scenario: The user gives a EOL page ID as parameter and wants only the data for the given EOL page ID.
                GIVEN an EOL page ID is given as parameter
                WHEN the EOL page ID is valid
                THEN the function should return a list containing the EOL trait data for only the given EOL page ID.
        """
        species_traits = eol.get_trait_data_for_eol_page_id('311544')
        assert len(species_traits) == 48

    @pytest.mark.parametrize(('eol_page_id', 'expected_number_of_traits'),
                             [('2926916', 64), ('1143547', 41)])
    def test_recursive_data_retrieval(self, eol, eol_page_id, expected_number_of_traits):
        """
        Feature: Retrieval of nested data from EOL CSV
            Scenario: The user gives a EOL page ID as parameter.
                GIVEN an EOL page ID is given as parameter
                WHEN the EOL page ID is valid
                    AND is a higher systematic level (e.g. Order or Family)
                    AND the function is provided with a recursion flag (e.g. recursive=True)
                THEN the function should return a list containing the EOL trait data for
                    - all direct children
                    - all nested children
                    - the given EOL page ID

        I hope, the numbers of traits are correct! If not, we have to discuss who is right (the code or Adrian [Spoiler:
        Most of the time, it is the code!]).
        """
        species_traits = eol.get_trait_data_for_eol_page_id(eol_page_id, recursive=True)
        assert len(species_traits) == expected_number_of_traits

    def test_correct_trait_data_is_retrieved(self, eol):
        """
        Feature: The module returns a set of EolData data class objects (https://docs.python.org/3/library/dataclasses.html)
            with the correct data.
            Scenario: The user expects to receive correct data.
                GIVEN a valid EOL page ID is given as parameter
                THEN the function should return a set of EolTrait objects with the correct data.
        """
        eol_page_id = '1143547'
        taxon_trait_data = eol.get_trait_data_for_eol_page_id(eol_page_id)

        assert isinstance(taxon_trait_data, set)
        assert trait_exists(eol_page_id, 'http://rs.tdwg.org/dwc/terms/habitat',
                            'http://purl.obolibrary.org/obo/ENVO_00000446', taxon_trait_data)
        assert trait_exists(eol_page_id, 'http://eol.org/schema/terms/Present', ' http://www.geonames.org/6252001',
                            taxon_trait_data)
        assert trait_exists(eol_page_id, 'http://eol.org/schema/terms/IntroducedRange',
                            'http://www.geonames.org/6251999', taxon_trait_data)

    def test_filtering_of_trait_data(self, eol):
        """
        Feature: The module filters the returned trait data by given filters.
            Scenario: The user only wants a subset of the available trait data.
                GIVEN a valid EOL page ID is given as parameter
                    AND a list of filter predicates is given as parameter
                THEN the function should return only a subset of the trait data of the given taxon, containing only
                    data fitting the given filter.
        """
        eol_page_id = '1143547'
        predicate_filters = ['http://rs.tdwg.org/dwc/terms/habitat', 'http://eol.org/schema/terms/Present']
        taxon_trait_data = eol.get_trait_data_for_eol_page_id(eol_page_id, filter_by_predicate=predicate_filters)

        assert isinstance(taxon_trait_data, set)
        assert trait_exists(eol_page_id, 'http://rs.tdwg.org/dwc/terms/habitat',
                            'http://purl.obolibrary.org/obo/ENVO_00000446', taxon_trait_data)
        assert trait_exists(eol_page_id, 'http://eol.org/schema/terms/Present', ' http://www.geonames.org/6252001',
                            taxon_trait_data)
        assert not trait_exists(eol_page_id, 'http://eol.org/schema/terms/IntroducedRange',
                                'http://www.geonames.org/6251999', taxon_trait_data)


def trait_exists(subject: str, predicate: str, obj: str, trait_data: Iterable[Triple]) -> bool:
    for trait in trait_data:
        if trait.subject == subject and trait.predicate == predicate and trait.object == obj:
            return True

    return False
