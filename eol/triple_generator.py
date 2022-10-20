# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 10:34:39 2022

@author: TAHIR
"""
from dataclasses import dataclass
from typing import Optional, Union, List, Iterable

import eol.variables as variables


@dataclass
class Triple:
    """Holds all information for a single triple."""

    subject: str
    predicate: str
    object: Union[str, int]
    eol_record_id: str
    unit: Optional[str] = None
    source_url: Optional[str] = None
    citation_text: Optional[str] = None

    def __hash__(self):
        return hash((self.subject, self.predicate, self.object, self.unit, self.source_url, self.citation_text))


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
        obj_value: str = triple_data.get(
            variables.VALUEURI_STRING
        )
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
            # Numeric values should be numeric, not strings
            if is_string_float_or_integer(quantity):
                quantity = float(quantity)

            triple = create_triple(triple_data, quantity, quantity_unit)
            triples.append(triple)

        obj = Objectclass_source()
        return obj.create_triple(triple_data, triples)


class Objectclass_source:
    """underclass TripleGenerator:
    if source is given"""

    def create_triple(self, triple_data, triples):
        """takes source if information is given and adds to the triples"""
        source_url = triple_data.get(variables.SOURCE_URL_STRING)
        citation_text = triple_data.get(variables.CITATION_STRING)
        if source_url is not None or citation_text is not None:
            for triple in triples:
                triple.source_url = source_url
                triple.citation_text = citation_text
        return triples  # gibt komplette triples-Liste zurück, chain of responsibility zu Ende


def create_triple(triple_data: dict, obj_value: [str, int, float], unit: str = None):
    subject = triple_data[variables.PAGE_ID_STRING]
    predicate = triple_data[variables.PREDICATE_STRING]
    eol_record_id = triple_data[variables.EOL_RECORD_ID]
    return Triple(
        str(subject), predicate, obj_value, eol_record_id=eol_record_id, unit=unit
    )


def deduplicate_triples(triples: Iterable[Triple]) -> List[Triple]:
    """data from list -> set -> sorted list"""
    triple_set = set(triples)  # data from list -> set (unsorted)
    return sorted(
        triple_set, key=lambda triple: (triple.subject, triple.predicate)
    )  # way of sorting
    # lambda takes triple and returns the triple's subject


def is_string_float_or_integer(string: str) -> float:
    """ Checks if a given string is an integer or a float number."""
    if isinstance(string, str):
        return string.replace(".", "", 1).isnumeric()
    else:
        return isinstance(string, (int, float))
