import pandas as pd
import requests
import lxml.html as lh
import csv

def get_tier_sheets():
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
    return tiers, rookiecontracts

def teamname_to_emoji(tid):
    with open('abbrev.csv', mode='r') as infile:
        reader = csv.reader(infile)
        dict = {rows[1]:rows[0] for rows in reader}
    return(dict[tid])

def emoji_to_teamname(tid):
    with open('abbrev.csv', mode='r') as infile:
        reader = csv.reader(infile)
        dict = {rows[0]:rows[1] for rows in reader}
    return(dict[tid])

def tid_from_teamname(data,name):
    for team in data['teams']:
        if name == team['region'] + ' ' + team['name']:
            return team['tid']
    return -1
def teamname_from_tid(data,name):
    for team in data['teams']:
        if name == team['tid']:
            return(team['region'] + ' ' + team['name'])
    return -1

def get_current_year(data):
    for iter in data['gameAttributes']:
        #print(iter)
        if iter['key'] == 'season':
            return iter['value']

def get_phase(data):
    for iter in data['gameAttributes']:
        if iter['key'] == 'phase':
            return iter['value']

def get_player(data,name,output=1):
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            return(player)
    if output==1:
        print('Couldnt find '+ str(name))
    return -1

def get_player_fa(data,name):
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            if player['tid'] != -1:
                continue
            if player['tid'] == -1:
                return 1
    return -1

def get_player_age(data,name,year):
    return year - get_player(data,name)['born']['year']

def get_player_ratings(data,name,year):
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            for seasons in player['ratings']:
                if seasons['season'] == year:
                    return seasons

    print('Couldnt find '+ str(name) +'\'s rating')
    return -1

def get_player_pos(data, name,year):
    for player in data['players']:
        if name == player['firstName'] + ' ' + player['lastName']:
            for seasons in player['ratings']:
                if seasons['season'] == year:
                    return seasons['pos']

    print('Couldnt find '+ name +'\'s position')
    return -1

def get_tier(data,name,year):
    try:
        #print(get_player_pos(name),get_player_ratings(name)['ovr'],str(get_player_age(name)))
        tiers,rookiecontracts=get_tier_sheets()
        return tiers[get_player_pos(data,name,year)].loc[get_player_ratings(data,name,year)['ovr']].at[str(get_player_age(data,name,year))]
    except:
        print('Could not find ' + str(name) + '\'s tier value.')
        return -1


def validate_player(data,name):
    if (name == 'c'):
        return -1
    if name[-1:] == ' ':
        name = name[:-1]
    if get_player(data,name,output=0) == -1:
        return validate_player(data,input("Couldn't find "+ str(name) + ". Perhaps the name is mispelled? Please enter the correct name or \"c\" to skip this offer.\n"))
    else:
        #if get_player_fa(name) == -1:

        return(name)

def sign_player(data,name,team,salary,years, year,rookie = False, phase=8):
    if type(team) == str:
        try:
            team = tid_from_teamname(data,emoji_to_teamname(team))
        except:
            print(name+': ' + team + ' is not a valid team name.')
            return -1
    if salary > 30:
        print(name+': The max salary is $30m')
        return -1
    if rookie == False:

        tiervalue = get_tier(data,name,year)
        # if(years == 1):
        #     print('allowed')
        if salary < tiervalue:
            print(name+': Salary below tier. The offer ' + str(salary) + ' was too low for the corresponding tier salary is $' + str(tiervalue) + 'M.')
            if name == 'Michael Joplin:':
                a=2
            else:
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
            #print(name)
            if rookie == True:
                if player['draft']['year'] != year:
                    continue
            if player['tid'] != -1:

                print(player['tid'])
                notFA=1
                continue
            else:
                player['contract']['amount'] = salary * 1000
                #print(salary)
                if phase < 6:
                    player['contract']['exp'] = year + years -1
                else:
                    player['contract']['exp'] = year + years
                player['tid'] = team
                player['watch'] = 'true'
                if(rookie==False):
                    print('\nSigned {0} to the {1} for ${2}m until {3}.'.format(player['firstName'] + ' ' + player['lastName']
                        ,teamname_from_tid(data,player['tid']),player['contract']['amount']/1000,player['contract']['exp']))
                    print("> **__FA Signing__**\n> {5} **{0}** ({6}/{7}) signs a {1}-year, ${2}M contract with the :{4}: @{3} \n".format(player['firstName'] + ' ' + player['lastName'],int(years),salary ,teamname_from_tid(data,team),
                    teamname_to_emoji(teamname_from_tid(data,team)), get_player_pos(data,name,year),int(get_player_ratings(data,name,year)['ovr']),int(get_player_ratings(data,name,year)['pot'])))

                return 1
    if notFA == 1:
        print(name  + ' is not a free agent.')
    print(name+': Could not find player '+name)
    return -1

def validate_playername_offers(data,sheet,year):
    sheet['ratings']=''
    sheet['ovr'] = 0

    for row in sheet.itertuples():
        #print(row.Index)
        realname = validate_player(data,row.player)
        if realname == -1 or get_player_fa(data,realname) == -1:
            continue
        sheet.iloc[row.Index,3] = realname
        sheet.iloc[row.Index,7] = str(get_player_pos(data,realname,year))+ ' ' + str(get_player_age(data,realname,year)) + 'y ' + str(get_player_ratings(data,realname,year)['ovr']) + ' ' + str(get_player_ratings(data,realname,year)['pot'])
        sheet.iloc[row.Index,8] = get_player_ratings(data,realname,year)['ovr']
        output = sheet
        #print(output)
    output[output.ovr>0][['time','user','team','player','salary','years','pitch']].sort_values('player').to_csv('newoffers.csv',index=False)
    return output[['team','player','ratings','salary','years','pitch', 'ovr']]



def print_multioffers(sheet,year):
    multioffers = sheet[sheet.duplicated('player',keep=False)]
    multioffers = multioffers[multioffers.ovr> 0]
    multioffers.sort_values('player')
    multioffers['random'] = ""
    multioffers['jackets'] = ""
    multioffers['brian'] = ""
    multioffers['spartan'] = ""
    multioffers['lam'] = ""
    multioffers['cubz'] = ""
    multioffers['sciipi'] = ""
    #, , multioffers['brian'], multioffers['spartan'], multioffers['lam']
    #,'jackets','brian','spartan','lam'
    print('Saving multioffers table... ')
    #print(multioffers[multioffers.ovr <=60])
    multioffers[['random','jackets','brian','spartan','cubz','sciipi','lam','team','player','ratings','salary','years','pitch']].sort_values('player').to_csv('multioffers.csv',index=False)

def sign_singleoffers(data,sheet,year):
    singleoffers = sheet.drop_duplicates(['player'],keep=False)
    print('Signing single offers... ')
    singleoffers= singleoffers.sort_values('ovr', ascending = True)
    for row in singleoffers.itertuples():
        # if row.ovr >= 60:
        #     sign_player(row.player,tid_from_teamname(row.team),row.salary,row.years)
        name = row.player
        if row.player[-1:] == ' ':
            name = row.player[:-1]

        sign_player(data,name,tid_from_teamname(data,row.team),row.salary,row.years,year)

def sign_multioffers(data,sheet,year):
    print('Signing multi offers... ')
    sheet = sheet.sort_values('salary')
    for row in sheet.itertuples():

        if row.winner == 'w':
            sign_player(data,row.player,tid_from_teamname(data,row.team),row.salary,row.years,year)


def rookie_resignings(data, rookiecontracts,year ):
    counter=1
    for player in data['players']:
            #if 'Chris Thompson' == player['firstName'] + ' ' + player['lastName']:
            #    print(player['draft']['year'])
            #    print(player['draft']['tid'],player['draft']['originalTid'])
            if player['draft']['year'] == year and player['draft']['round']>0:
                picknumber = 32*(player['draft']['round']-1) +player['draft']['pick']
                salary = rookiecontracts.iloc[picknumber-1].at['contract']
                if player['draft']['round'] == 1:
                    player['born']['loc'] = player['born']['loc'] + ' - {0} TO'.format(year+4)
                sign_player(data,player['firstName'] + ' ' + player['lastName'],player['draft']['tid'],salary,3, year, rookie = True)
                counter +=1
    print('Signed ' + str(counter-1) + ' rookies.')

def extend_options(data,draft, excluded):
    i=1
    for player in data['players']:
        name = player['firstName'] + ' ' + player['lastName']
        if player['draft']['year'] == draft and player['draft']['round']==1 and name not in excluded:
            player['contract']['exp'] += 1
            i+=1
    print('Extended ' + str(i-1) + ' ' + str(season) + ' options.')
