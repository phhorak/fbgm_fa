import csv
import os
import pandas as pd
import numpy as np
import json
import codecs


export = open('export.json')
data = json.load(codecs.open('export.json', 'r+', 'utf-8-sig'))


offers= pd.read_csv('offers.csv', names=['time','user','team','player','salary','years','pitch'],header=0)

pd.options.mode.chained_assignment = None


#reading tier tables

tiers= {}
tiers['QB'] = pd.read_csv("tiers/QBTiers.csv", index_col=0)
tiers['OL'] = pd.read_csv("tiers/OLTiers.csv", index_col=0)
tiers['WR'] = pd.read_csv("tiers/WRTiers.csv", index_col=0)
tiers['TE'] = pd.read_csv("tiers/TETiers.csv", index_col=0)
tiers['RB'] = pd.read_csv("tiers/RBTiers.csv", index_col=0)
tiers['DL'] = pd.read_csv("tiers/DLTiers.csv", index_col=0)
tiers['LB'] = pd.read_csv("tiers/LBTiers.csv", index_col=0)
tiers['CB'] = pd.read_csv("tiers/CBTiers.csv", index_col=0)
tiers['S'] = pd.read_csv("tiers/STiers.csv", index_col=0)
tiers['P'] = pd.read_csv("tiers/KPTiers.csv", index_col=0)
tiers['K'] = pd.read_csv("tiers/KPTiers.csv", index_col=0)
rookiecontracts = pd.read_csv("tiers/rookiecontracts.csv", index_col=0)
print(rookiecontracts)
#converting between emojis like 'mxc' to 'Mexico City Aztecs'

with open('abbrev.csv', mode='r') as infile:
    reader = csv.reader(infile)
    with open('coors_new.csv', mode='w') as outfile:
        emoji_to_teamname = {rows[0]:rows[1] for rows in reader}

with open('abbrev.csv', mode='r') as infile:
    reader = csv.reader(infile)
    with open('coors_new.csv', mode='w') as outfile:
        teamname_to_emoji = {rows[1]:rows[0] for rows in reader}

#converting between team id and team name

def tid_from_teamname(name):
    for team in data['teams']:
        if name == team['region'] + ' ' + team['name']:
            return team['tid']
    return -1

def teamname_from_tid(name):
    for team in data['teams']:
        if name == team['tid']:
            return(team['region'] + ' ' + team['name'])
    return -1

#player queries

def get_player(name,output=1):
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            return(player)
    if output==1:
        print('Couldnt find '+ str(name))
    return -1

def get_player_age(name):
    return current_year - get_player(name)['born']['year']

def get_player_ratings(name):
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            for seasons in player['ratings']:
                if seasons['season'] == current_year:
                    return seasons

    print('Couldnt find '+ str(name) +'\'s rating')
    return -1


def get_player_pos(name):
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            for seasons in player['ratings']:
                if seasons['season'] == current_year:
                    return seasons['pos']

    print('Couldnt find '+ name +'\'s position')
    return -1

def get_tier(name):
    try:
        #print(get_player_pos(name),get_player_ratings(name)['ovr'],str(get_player_age(name)))
        return tiers[get_player_pos(name)].loc[get_player_ratings(name)['ovr']].at[str(get_player_age(name))]
    except:
        print('Could not find ' + str(name) + '\'s tier value.')


def sign_player(name,team,salary,years,rookie = False):
    if type(team) == str:
        try:
            team = tid_from_teamname(emoji_to_teamname[team])
        except:
            print(name+': ' + team + ' is not a valid team name.')
            return -1
    if salary > 30:
        print(name+': The max salary is $30m')
        return -1
    if rookie == False:
        tiervalue = get_tier(name)
        if salary < tiervalue:
            print(name+': Salary below tier. The corresponding tier salary is $' + str(tiervalue) + 'M.')
            return -1



    if years > 5:
        print(name+': The max amount of years is 5')
        return -1
    if team < 0 or team > 31:
        print(name+': TID must be between 0 and 31')
        return -1
    notFA=0
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            if rookie == True:
                if player['draft']['year'] != current_year:
                    continue
            if player['tid'] != -1:
                print(player['tid'])
                notFA=1
                continue
            else:
                player['contract']['amount'] = salary * 1000
                player['contract']['exp'] = current_year + years
                player['tid'] = team
                print('\nSigned {0} to the {1} for ${2}m until {3}.'.format(player['firstName'] + ' ' + player['lastName']
                    ,teamname_from_tid(player['tid']),player['contract']['amount']/1000,player['contract']['exp']))
                print("> **__FA Signing__**\n> {5} **{0}** signs a {1}-year, ${2}M contract with the :{4}: @{3} \n".format(player['firstName'] + ' ' + player['lastName'],years,salary ,teamname_from_tid(team),teamname_to_emoji[teamname_from_tid(team)], get_player_pos(name)))


                return 1
    if notFA == 1:
        print(name  + ' is not a free agent.')
    print(name+': Could not find player '+name)
    return -1

def validate_player(name):
    if (name == 'c'):
        return -1
    if get_player(name,output=0) == -1:
        return validate_player(input("Couldn't find "+ str(name) + ". Perhaps the name is mispelled? Please enter the correct name or \"c\" to cancel.\n"))
    else:
        return(name)

def validate_playername_offers(sheet):
    sheet['ratings']=''
    sheet['ovr'] = 0

    for row in sheet.itertuples():
        #print(row.Index)
        realname = validate_player(row.player)
        if realname == -1:
            continue
        sheet.iloc[row.Index,3] = realname
        sheet.iloc[row.Index,7] = str(get_player_pos(realname))+ ' ' + str(get_player_age(realname)) + 'y ' + str(get_player_ratings(realname)['ovr']) + ' ' + str(get_player_ratings(realname)['pot'])
        sheet.iloc[row.Index,8] = get_player_ratings(realname)['ovr']
        output = sheet[['team','player','ratings','salary','years','pitch', 'ovr']]
    return output

def print_multioffers(sheet):
    multioffers = sheet[sheet.duplicated('player',keep=False)]
    multioffers.sort_values('player')
    multioffers['random'] = ""
    multioffers['jackets'] = ""
    multioffers['brian'] = ""
    multioffers['spartan'] = ""
    multioffers['lam'] = ""
    #, , multioffers['brian'], multioffers['spartan'], multioffers['lam']
    #,'jackets','brian','spartan','lam'
    print('Saving multioffers table... ')
    multioffers[['random','jackets','brian','spartan','lam','team','player','ratings','salary','years','pitch']].sort_values('player').to_csv('multioffers.csv',index=False)


def sign_singleoffers(sheet):
    singleoffers = sheet.drop_duplicates(['player'],keep=False)
    print('Signing single offers... ')
    singleoffers= singleoffers.sort_values('ovr', ascending = True)
    for row in singleoffers.itertuples():
        if row.ovr :
            sign_player(row.player,tid_from_teamname(row.team),row.salary,row.years)


def rookie_resignings(season):
    counter=1
    for player in data['players']:
            #if 'Chris Thompson' == player['firstName'] + ' ' + player['lastName']:
            #    print(player['draft']['year'])
            #    print(player['draft']['tid'],player['draft']['originalTid'])
            if player['draft']['year'] == season and player['draft']['round']>0:
                picknumber = 32*(player['draft']['round']-1) +player['draft']['pick']
                salary = rookiecontracts.iloc[picknumber-1].at['contract']
                if player['draft']['round'] == 1:
                    player['born']['loc'] = player['born']['loc'] + ' - {0} TO'.format(current_year+4)
                sign_player(player['firstName'] + ' ' + player['lastName'],player['draft']['tid'],salary,3, rookie = True)



current_year=data['gameAttributes'][44]['value']
#rookie_resignings(2027)
#newoffers = pd.DataFrame({'A' : []})
#print(get_player('Chris Thompson'))
newoffers = validate_playername_offers(offers)
print_multioffers(newoffers)
sign_singleoffers(newoffers)


#print(validate_player('barney'))
#print(multioffers.sort_values('player'))

#sign_player('Marc Copp',15,salary=12,years=3)
#sign_player('Quincy McAllister','mxc',salary=30,years=3)
#sign_player('Shaheen Douglas','san',12,3)
#sign_player('Steven Compton', 'was', 10,2)
#sign_player('Eric Mosure', 'nyc', 2,1)
#sign_player('Jaylen Brown', 'xxx', 1, 1)




#print(tiers['OL'].head(50))






jsonoutput = open('edited.json', mode='w')
json.dump(data, jsonoutput, indent=4)


print('\n Created updated export.')
