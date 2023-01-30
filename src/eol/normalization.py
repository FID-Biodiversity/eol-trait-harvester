from copy import copy

import eol.variables as variables
from eol.triple_generator import TripleGenerator


class Normalizer:
    """A base class for all normalization processes of EOL data sources.
    Only keys that need to be normalized/deleted have to be provided. The
    normalized keys have to be unique. If not, data will be overwritten.
    """

    # A dictionary providing the un-normalized key that is exchanged by the given value
    normalized_keys = {}

    # A list of keys to be delete
    delete_keys = []

    def normalize(self, data: dict) -> dict:
        """Normalizes the keys in the given data.
        This function returns a new dictionary.
        First, keys are normalized. Subsequently, keys are deleted from the data.
        """
        data_copy = copy(data)

        for old_key, normalized_key in self.normalized_keys.items():
            replace_key_by_new_key(old_key, normalized_key, data_copy)

        for key_to_delete in self.delete_keys:
            if key_to_delete in data_copy:
                del data_copy[key_to_delete]

        return data_copy


class EolTraitCsvNormalizer(Normalizer):
    """This class normalizes the data provided by the EolTraitCsvHandler."""

    normalized_keys = {
        "citation": variables.CITATION_STRING,
        "eol_pk": variables.EOL_RECORD_ID,
        "literal": variables.LITERAL_STRING,
        "normal_measurement": variables.NORMAL_MEASURE_STRING,
        "normal_units_uri": variables.NORMAL_UNITS_URI_STRING,
        "predicate": variables.PREDICATE_STRING,
        "source": variables.SOURCE_URL_STRING,
        "units_uri": variables.NORMAL_UNITS_URI_STRING,
        "value_uri": variables.VALUE_URI_STRING,
        "page_id": variables.PAGE_ID_STRING,
    }


class EolTraitApiNormalizer(Normalizer):
    """This class normalizes the data provided by the EolTraitApiHandler."""

    normalized_keys = {
        "t.eol_pk": variables.EOL_RECORD_ID,
        "obj.uri": variables.VALUE_URI_STRING,  # obj.name auch vorhanden
        "p.citation": variables.CITATION_STRING,  # citation von PAGE-Knoten
        "p.page_id": variables.PAGE_ID_STRING,
        "pred.uri": variables.PREDICATE_STRING,  # pred.name auch vorhanden
        "t.citation": variables.CITATION_STRING,  # citation von TRAITS-Knoten
        "t.literal": variables.LITERAL_STRING,
        "t.normal_measurement": variables.NORMAL_MEASURE_STRING,
        "t.source": variables.SOURCE_URL_STRING,
        "t.normal_units": variables.NORMAL_UNITS_URI_STRING,
        "units.uri": variables.NORMAL_UNITS_URI_STRING,  # units.name auch vorhanden
    }


def replace_key_by_new_key(old_key: str, new_key: str, data: dict) -> None:
    """Assigns the new_key the value of old_key and removes old_key from the data.
    The exchange is done in-place.
    In case of a new_key value is not None, it will overwrite any already existing
    values associated with new_key. If a new_key value that is not None would
    overwrite another not None value associated with new_key that is
    already in the data, a ValueError will be raised.
    """
    if old_key == new_key:
        return

    if old_key in data:
        existing_new_key_value = data.get(new_key)

        # Do not overwrite an existing new_key with a not-None value.
        if existing_new_key_value is not None:
            if data[old_key] is not None and data[old_key] != data[new_key]:
                raise ValueError(
                    f"Multiple keys map to the value {new_key}, but both have "
                    f"valid (not-None) values!"
                )
        else:
            data[new_key] = data[old_key]

        del data[old_key]


if __name__ == "__main__":
    # How to use the DataHandler and Normalizer in conjunction

    from pprint import pprint

    from src.eol.handlers import EolTraitApiHandler, EolTraitCsvHandler

    # Get the data from the data source
    # Watch out! The `iterate_data_by_key` method returns a Generator. To get
    # the single elements from it, you have to call either next() on the
    # same Generator object repeatedly or use it in a for-loop.
    # Example:
    #           for elem in handler.iterate_data_by_key(key='page_id', value=45258442):
    #               # do stuff with elem (which is an data element), no need to
    #               # call next, in this case!
    handler = EolTraitCsvHandler("../tests/data/test_eol_traits.csv")
    non_normalized_csv_data = next(
        handler.iterate_data_by_key(key="page_id", value=45258442)
    )

    # Normalize the data
    normalizer = EolTraitCsvNormalizer()
    normalized_data = normalizer.normalize(non_normalized_csv_data)

    # Generate triples
    triple_generator = TripleGenerator()
    triples = triple_generator.create_triples(normalized_data)

    pprint("Generated Triples")
    pprint(triples)

    pprint("Data from CSV File")
    pprint(normalized_data)

    # Example of how to get data from the EOL API
    import os

    from dotenv import load_dotenv

    load_dotenv("../../tests/.env")

    eol_api_token = f"JWT {os.environ['EOL_API_TOKEN']}"
    handler = EolTraitApiHandler(eol_api_token)

    # Watch out! The key has to be the Cypher variable you are specifically
    # interested. However, in our cases, you  probably only need to change the
    # `value` parameter anyway. The consideration to use next or a for-loop (see above),
    # applies here too.
    non_normalized_api_data = next(
        handler.iterate_data_by_key(
            key="pred.uri", value="http://purl.obolibrary.org/obo/RO_0002303"
        )
    )

    normalizer = EolTraitApiNormalizer()
    normalized_data = normalizer.normalize(non_normalized_api_data)

    pprint("Data from EOL API")
    pprint(normalized_data)
