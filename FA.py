import csv
import os
import pandas as pd
import numpy as np
import json
import codecs
from helpers import *
import time

export = open('export.json')
data = json.load(codecs.open('export.json', 'r+', 'utf-8-sig'))

offers= pd.read_csv('offers.csv', names=['time','user','team','player','salary','years','pitch'],header=0)
#multioffers = pd.read_csv('voting.csv')
pd.options.mode.chained_assignment = None

current_season=get_current_year(data)
current_phase=get_phase(data)

#This is to automatically resign rookies of a specific draft year (here 2028)
#rookie_resignings(data, rookiecontracts,  current_season)

#These 3 lines process the offers.csv table.
#All multioffers are saved for voting in a seperate sheet called "multioffers.csv". Download that and upload it to google sheets, then post in discord for voting
#All single offers are attempted to be signed (doesnt work if below tier or isn't a free agent.)

newoffers = validate_playername_offers(data,offers, current_season)
print_multioffers(newoffers,current_season)
sign_singleoffers(data,newoffers,current_season)

# This function is to extend rookie options of a specific draft
# second argument (2025) is the year
# third argument "['Beau Catlin', 'Camden Williams']" are the guys that had their TO refused. (Won't be extended)

# extend_options(data,2025, [])

# This is to sign individual players, for someone thats missing in the sheet, or when you finished voting on multioffers you can write one of these lines per player.
# arguments are: 2. player name, 3. team ID or team emoji, 4. salary in millions, 5. amount of year

# sign_player(data,'Adam Scales','den',salary=30,years=1, year=current_season)





jsonoutput = open('edited.json', mode='w')
#this line decides if you want to produce an updated export in the end or not, if you just want to try around you can disable it.
# If its disabled it will still give you all the messages like "xxx is not a free agent" or "signed xxx to a yy contract" but it won't save an export anywhere
#json.dump(data, jsonoutput, indent=0)


print('\n Created updated export.')
