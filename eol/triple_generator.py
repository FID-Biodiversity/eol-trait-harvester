# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 10:34:39 2022

@author: TAHIR
"""
from typing import Optional

import eol.variables as variables
from dataclasses import dataclass

# chain of command, design of command
# chain of responsibility
# one class per object-combination: 3 known object-combinations


@dataclass
class Triple:
    """Holds all information for a single triple."""

    subject: str
    predicate: str
    object: str
    unit: Optional[str] = None
    # TODO: Add source incl. tests
    
    def __hash__(self):
        return hash((self.subject, self.predicate, self.object))


class TripleGenerator:
    """Generates Triple objects from a given normalized dataset."""

    def create_triples(self, triple_data):
        obj = Objectclass_objuri()
        triples = []
        triples = obj.create_triple(triple_data, triples)
        return deduplicate_triples(triples)
    

class Objectclass_objuri:
    """underclass TripleGenerator:
    if object information is in obj.uri and obj.name"""

    def create_triple(self, triple_data, triples):
        obj_value = triple_data.get(variables.VALUEURI_STRING)#gibt None zurück wenn kein Wert drin ist
        if obj_value is not None:
            triple = create_triple(triple_data, obj_value)
            triples.append(triple)

        obj = Objectclass_tliteral()
        return obj.create_triple(triple_data, triples)


class Objectclass_tliteral:
    """underclass TripleGenerator:
    if object information is in t.literal"""

    def create_triple(self, triple_data, triples):
        obj_value = triple_data.get(variables.LITERAL_STRING)
        if obj_value is not None:
            triple = create_triple(triple_data, obj_value)
            triples.append(triple)

        obj = Objectclass_meas_units()
        return obj.create_triple(triple_data, triples)


class Objectclass_meas_units:
    """underclass TripleGenerator:
    if object information is in t.normal_measurement, units.uri, units.name"""

    def create_triple(self, triple_data, triples):
        quantity = triple_data.get(variables.NORMALMSM_STRING)
        quantity_unit = triple_data.get(variables.NORMAL_UNITSURI_STRING)
        if quantity is not None and quantity_unit is not None:
            triple = create_triple(triple_data, quantity, quantity_unit)
            triples.append(triple)
        return triples  # gibt komplette triples-Liste zurück, chain of responsibility zu Ende


def create_triple(triple_data: dict, obj_value: str, unit: str = None):
    subject = triple_data[variables.PAGE_ID_STRING]
    predicate = triple_data[variables.PREDICATE_STRING]
    return Triple(str(subject), predicate, obj_value, unit=unit)


def deduplicate_triples(triples):
    """ data from list -> set -> sorted list """
    triple_set = set(triples)  # data from list -> set (unsorted)
    return sorted(triple_set, key=lambda triple: (triple.subject, triple.predicate))  # way of sorting
    # lambda takes triple and returns the triple's subject
