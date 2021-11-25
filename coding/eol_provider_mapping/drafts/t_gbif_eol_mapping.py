"""
testing read in with pandas as chunks

"""

#import pandas as pd
import csv
#import time
#import csv


#start = time.time() #Laufzeitmessung Startzeit // REMOVE TO SHOW TIME

"""
#TRY1
chunksize = 10 ** 6
for chunk in pd.read_csv('traits.csv', chunksize=chunksize):
    process(chunk)
"""

"""
#TRY2
df = csv.reader(open('test_traits.csv', 'rb'))
lines = list(df)
print(lines[:100])
"""


#TRY3
datafile = "provider_ids.csv"

with open(datafile, 'r',) as f:
    read_operation = csv.reader(f)
    lines = list(read_operation)
    print(lines[:100])



