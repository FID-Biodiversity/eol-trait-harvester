from copy import copy
from eol.triple_generator import TripleGenerator
import eol.variables as variables


class Normalizer:
    """ A base class for all normalization processes of EOL data sources.
        Only keys that need to be normalized/deleted have to be provided. The normalized keys have to be unique. If not,
        data will be overwritten.
    """

    # A dictionary providing the un-normalized key that is exchanged by the given value
    normalized_keys = {}

    # A list of keys to be delete
    delete_keys = []

    def normalize(self, data: dict) -> dict:
        """ Normalizes the keys in the given data.
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
    """ This class normalizes the data provided by the EolTraitCsvHandler. """
    normalized_keys = {'page_id': variables.PAGE_ID_STRING,  # importiert aus variables.py
                       'predicate': variables.PREDICATE_STRING, 
                       'value_uri': variables.VALUEURI_STRING,
                       'literal': variables.LITERAL_STRING,
                       'normal_measurement': variables.NORMALMSM_STRING,
                       'normal_units_uri': variables.NORMAL_UNITSURI_STRING,
                       'units_uri': variables.NORMAL_UNITSURI_STRING
                       }
                        #normal_units_uri, normal_units, units_uri, units #nur verwendbare Daten
                        #normal_units_uri, units_uri


class EolTraitApiNormalizer(Normalizer):
    """ This class normalizes the data provided by the EolTraitApiHandler. """
    pass
    #eol.org variablen 


def replace_key_by_new_key(old_key: str, new_key: str, data: dict) -> None:
    """ Assigns the new_key the value of old_key and removes old_key from the data.
        The exchange is done in-place.
    """
    if old_key == new_key:
        return

    if old_key in data:
        data[new_key] = data[old_key]
        del data[old_key]


if __name__ == '__main__':
    # How to use the DataHandler and Normalizer in conjunction

    from eol.handlers import EolTraitCsvHandler, EolTraitApiHandler
    from pprint import pprint

    # Get the data from the data source
    # Watch out! The `iterate_data_by_key` method returns a Generator. To get the single elements from it,
    # you have to call either next() on the same Generator object repeatedly or use it in a for-loop.
    # Example:
    #           for elem in handler.iterate_data_by_key(key='page_id', value=45258442):
    #               # do stuff with elem (which is an data element), no need to call next, in this case!
    handler = EolTraitCsvHandler('../tests/data/test_eol_traits.csv')
    non_normalized_csv_data = next(handler.iterate_data_by_key(key='page_id', value=45258442))

    # Normalize the data
    normalizer = EolTraitCsvNormalizer()
    normalized_data = normalizer.normalize(non_normalized_csv_data)

    # Generate triples
    triple_generator = TripleGenerator()
    triples = triple_generator.create_triples(normalized_data)

    pprint('Generated Triples')
    pprint(triples)

    pprint('Data from CSV File')
    pprint(normalized_data)

    # Example of how to get data from the EOL API
    from dotenv import load_dotenv
    import os
    load_dotenv('../tests/.env')

    eol_api_token = f"JWT {os.environ['EOL_API_TOKEN']}"
    handler = EolTraitApiHandler(eol_api_token)

    # Watch out! The key has to be the Cypher variable you are specifically interested. However, in our cases, you
    # probably only need to change the `value` parameter anyway.
    # The consideration to use next or a for-loop (see above), applies here too.
    non_normalized_api_data = next(handler.iterate_data_by_key(key='pred.uri',
                                                               value='http://purl.obolibrary.org/obo/RO_0002303'))

    normalizer = EolTraitApiNormalizer()
    normalized_data = normalizer.normalize(non_normalized_api_data)

    pprint('Data from EOL API')
    pprint(normalized_data)
