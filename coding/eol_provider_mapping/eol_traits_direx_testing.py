# -*- coding: utf-8 -*-
"""
EOL Traits Data
EOL-triple-extraction

This program extracts information from a traits file and returns a triple:
(subject, predicate, object)
in the form
(page_id, predicate, uri_value)

traits file used from eol.org:
https://editors.eol.org/other_files/SDR/traits_all.zip

"""

__author__ = "Ischa Tahir"
__copyright__ = "Senckenberg Gesellschaft für Naturforschung, \
                 Senckenberganlage 25, 60325 Frankfurt, Germany"

import csv

eol_page_id = "45258442"

with open("test_traits.csv", encoding='utf-8') as csvfile:
    csv_text = csv.reader(csvfile)
    for line in csv_text:
        if eol_page_id in line:
            break
            check_eol_page_id = line[1]
            if check_eol_page_id == eol_page_id:
                print("True")
                #print(line, "LINE FOUND")# for testing. check if correct line is found
                print(line[1], "eol-page-id")#for testing. check if correct page_id is found
                predicate = line[6]#for testing. check which predicate found in line
                print(predicate, "predicate")#for testing
            else:
                print("Error. page_id does not exist or is in wrong position")

global end_object;

def object_definition(predicate):
    """
    Analyses predicate to decide which object to choose.
    More predicates can be added and specified.
    """
    if "habitat" in predicate:#habitat
        #http://rs.tdwg.org/dwc/terms/habitat
        #then choose following cols
        end_object = line[8]
        return end_object
        #print(end_object)
        
    if "Present" in predicate:#geographical distribution
        #http://eol.org/schema/terms/Present
        #then choose following cols
        end_object = line[8]
        return end_object
    
    else:
        print("predicate not defined")
        return False
    

end_object = object_definition(predicate)
#print(end_object)#for testing. check which object is found in line

result_triple = (eol_page_id, predicate, end_object)
print(result_triple)



    