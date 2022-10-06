# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 10:34:39 2022

@author: TAHIR
"""
#import normalization
import variables
from dataclasses import dataclass

#chain of command, design of command
#chain of responsibility
#one class per object-combination: 3 known object-combinations

@dataclass
class Triple:
    subject: str
    predicate: str
    object_str: str



class TripleGenerator:
    def create_triples(self, normalized_data):
        triples = []
        for triple_data in normalized_data:
            print(triple_data)
            obj = Objectclass_objuri()
            t = obj.create_triple(triple_data, triples)
            triples.extend(t)#fügt Objekte der Liste in t ein. Kreiert fertige End-Triples-Liste
        print(triples)
        return triples
    

class Objectclass_objuri():
    
    """ underclass TripleGenerator:
        if object information is in obj.uri and obj.name """
    def create_triple(self, triple_data, triples):
        obj_value = triple_data[variables.VALUEURI_STRING]
        if obj_value is not None:
            triple = create_triple(triple_data, obj_value)
            triples.append(triple)
            
        obj = Objectclass_tliteral()
        return obj.create_triple(triple_data, triples)
                
            
    
class Objectclass_tliteral():
    """ underclass TripleGenerator:
    if object information is in t.literal """
    def create_triple(self, triple_data, triples):
        obj_value = triple_data[variables.LITERAL_STRING]
        if obj_value is not None:
            triple = create_triple(triple_data, obj_value)
            triples.append(triple)
            
        obj = Objectclass_meas_units()
        return obj.create_triple(triple_data, triples)
    
class Objectclass_meas_units():
    """ underclass TripleGenerator:
    if object information is in t.normal_measurement, units.uri, units.name """
    def create_triple(self, triple_data, triples):
        obj_value1 = triple_data[variables.NORMALMSM_STRING]
        obj_value2 = triple_data[variables.NORMAL_UNITSURI_STRING]
        if obj_value1 is not None and obj_value2 is not None:
            triple1 = create_triple(triple_data, obj_value1)
            triple2 = create_triple(triple_data, obj_value2)
            triples.append(triple1)
            triples.append(triple2)
        return triples #gibt komplette triples-Liste zurück, chain of responsibility zu Ende
    
def create_triple(triple_data, obj_value):
    subject = triple_data[variables.PAGE_ID_STRING]
    predicate = triple_data[variables.PREDICATE_STRING]
    return Triple(subject, predicate, obj_value)

#(subject, predicate, obj)
#[(subject, predicate, obj1), (subject, predicate, obj2)]

        
