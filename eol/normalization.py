from copy import copy
#from triplegenerator import TripleGenerator
import triplegenerator
import variables


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
               
        print(self.normalized_keys)

        return data_copy


class EolTraitCsvNormalizer(Normalizer):
    """ This class normalizes the data provided by the EolTraitCsvHandler. """
    normalized_keys = {'page_id': variables.PAGE_ID_STRING,#importiert aus variables.py
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
    if old_key in data:
        data[new_key] = data[old_key]
        del data[old_key]


if __name__ == '__main__':
    # How to use the DataHandler and Normalizer in conjunction
    from handlers import EolTraitCsvHandler#, EolTraitApiHandler
    from pprint import pprint

    # Get the data from the data source
    handler = EolTraitCsvHandler('../tests/data/test_eol_traits.csv')#Object instanziert
    non_normalized_data = handler.get_data_filtered_by_value(key='page_id', value=45258442)
    ###non_normalized_data

    # Normalize the data
    normalizer = EolTraitCsvNormalizer()
    normalized_data = normalizer.normalize(non_normalized_data)
    
    #TRIPLEGENERATOR: input
    triple_generator = triplegenerator.TripleGenerator()
    triples = triple_generator.create_triples(normalized_data)

    pprint(normalized_data)
