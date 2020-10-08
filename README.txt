Harkirat Rakhra 
0969501
Cloud Computing Assignment 1

PART 1
------------------------------------
PYTHON MODULES:
boto3, configparser, os, csv, sys, prettytable

ANY BASIC COMMANDS THAT YOUR PROGRAM DOES NOT HANDLE:
I was not able to get ls -l fully functional, but it still displays some information. I had trouble getting information for buckets.

ERROR CONDITIONS CHECKED:
My program checks for all the conditions stated in the pdf. Trying to execute cmd without logging it, using a command not listed ...

COMMENTS:
I am not 100% sure that I implemented my login correctly when a session token is not given. Since I do not have a real account I could 
not test this portion.(session tokens are required for me :( )

PART 2
------------------------------------
Primary Key is Commodity 
commodity, variableyear(variable+'/'+year), mfactor,units, value, variable,year
loadtable does not load encodings.csv. To load encodings.csv -> python3 createEncodingTable.py (need to run this before query)

query is run by stdin
program reads in valuse from encodings createEncodingTable
the program checks for errors stated inside the pdf
I used my ~.aws/config to create a boto3 resource.
