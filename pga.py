import copy
import math
import pprint
import pandas as pd
import matplotlib as plt
import pylab

#Read Acquire log file
with open('C:\\4. Github\\PGA\\log3.txt') as f:
    raw_lines = f.read().splitlines()


companies = ['Luxor', 'Tower', 'Worldwide', 'Festival', 'American', 'Continental', 'Imperial']

def is_adjacent(tile1, tile2):
    """
    Check if two tiles are adjacent. E.g. '3A' and '3B' are adjacent; '3F' and '5F' are not
    """
    x1 = int(tile1[:-1])
    y1 = ord(tile1[-1])

    x2 = int(tile2[:-1])
    y2 = ord(tile2[-1])

        
    if abs(x1 - x2) == 1 and abs(y1 - y2) == 0:
        return(True)
    elif abs(x1 - x2) == 0 and abs(y1 - y2) == 1:
        return(True)
    return(False)

def build_game_log(raw_lines):
    
    # Scoreboard
    nInclude = 0
    scoreboard = []
    for line in raw_lines:
        if  line.startswith('Player'):
            nInclude = 1
        elif 'Price ($00)' in line:
            nInclude = 0
        if nInclude == 1:
            scoreboard.append(line)

    # Players
    players = []
    for line in scoreboard[1:-2]:
        # Scoreboard lines can be separated by tab or space. Handle either way
        if '\t' in line:
            player = line.split('\t')[0]
        else:
            player = line.split(' ')[0]
        players.append(player)


    ## Create board & constants
    unplayed_tiles = {str(x)+str(y) for x in range(1,13,1) for y in 'ABCDEFGHI'}
    played_tiles = set()

    #companies = ['Luxor', 'Tower', 'Worldwide', 'Festival', 'American', 'Continental', 'Imperial']
    gameplay = []
    turns = {}
    current_shares = {player:{company:0 for company in companies} for player in players}

    turn_number = 0
    nInclude = 0
    for line in raw_lines:

        ### Starting tiles 
        if 'drew position tile ' in line:
            tile = line.replace('.', '').split(' ')[-1]
            played_tiles.add(tile)
            unplayed_tiles.remove(tile)

        ### Main Gameplay
        if line in players:
            nInclude = 1
        elif 'Game over' in line or 'Global Chat' in line or 'Game Chat' in line:
            nInclude = 0

        ### Update turns log
        if nInclude == 1:
            gameplay.append(line)

            if line in players:
                ### End off previous turn
                if turn_number != 0:
                    turns[turn_number]['shares'] = copy.deepcopy(current_shares)
                    turns[turn_number]['tiles_played'] = copy.copy(played_tiles)

                ### Start of new turn
                turn_number += 1
                current_player = line
                turns[turn_number] = {'player':current_player,
                                      'purchased_shares': {},
                                      'is_merger':False,
                                      'bonus_paid':{},
                                      'sold_shares':[],
                                      'is_founding':False,
                                      'tile_played':None,
                                      'merger_survivor':None,
                                      'merger_lost':set(),
                                      'text':[line],
                                      'shares':None,
                                      'tiles_played':None,
                                      'turn_number':turn_number}
            else:
                turns[turn_number]['text'].append(line)

            # Tile played
            if 'drew tile ' in line or 'played tile ' in line:
                if 'You ' not in line:
                    tile = line.split(' ')[-1][:-1]
                    turns[turn_number]['tile_played'] = tile
                    unplayed_tiles.remove(tile)
                    played_tiles.add(tile)

            # Merger
            if 'merged ' in line:
                turns[turn_number]['is_merger'] = True

            elif turns[turn_number]['is_merger']:
                if 'received a $' in line:
                    bonus_company = line.split(' ')[-2]
                    turns[turn_number]['merger_lost'].add(bonus_company)
                    player = line.split(' ')[0]
                    bonus = int(line.split(' ')[-3][1:])
                    if player in turns[turn_number]['bonus_paid'].keys():
                        turns[turn_number]['bonus_paid'][player] += bonus
                    else:
                        turns[turn_number]['bonus_paid'][player] = bonus
                    

                # Go back and infer merger survivor
                for line in turns[turn_number]['text']:
                    if 'merged ' in line:
                        for company in companies:
                            if company in line and company not in turns[turn_number]['merger_lost']:
                                turns[turn_number]['merger_survivor'] = company


            ### Update Chain sizes
            # Done in part 2

            ### Update shares
            # Purchased shares
            purchased_shares = {}
            if 'purchased ' in line:
                splt = line.replace('.', '').replace(',', '').split(' ')
                player = splt[0]
                for i in range(len(splt[2:])):
                    if splt[2+i] == '1' or splt[2+i] == '2' or splt[2+i] == '3':
                        qty = int(splt[2+i])
                        company = splt[3+i]
                        current_shares[player][company] += qty
                        purchased_shares[company] = qty
                turns[turn_number]['purchased_shares'] = purchased_shares

            # Founding bonus stock
            if 'formed ' in line:
                turns[turn_number]['is_founding'] = True
                splt = line.replace('.', '').split(' ')
                player = splt[0]
                company = splt[-1]
                current_shares[player][company] += 1

            # Traded or sold shares
            if 'traded ' in line:
                splt = line.replace('.', '').split(' ')
                player = splt[0]
                company = splt[-2]
                qty_traded = int([splt[i+1] for i in range(len(splt)) if splt[i] == 'traded'][0])
                if qty_traded > 0:
                    survivor = turns[turn_number]['merger_survivor']
                    current_shares[player][survivor] += int(qty_traded/2)
                qty_sold = int([splt[i+1] for i in range(len(splt)) if splt[i] == 'sold'][0])
                turns[turn_number]['sold_shares'].append([player, company, qty_sold])
                current_shares[player][company] -= (qty_traded + qty_sold)

            ### Replaced tiles
            # Skipped for now

            ### Update cash & net worth
            # Done in part 2

    # Finish off final turn
    turns[len(turns)]['shares'] = copy.deepcopy(current_shares)
    turns[len(turns)]['tiles_played'] = copy.copy(played_tiles)
 
    return( {'log':turns, 'players': players} )

    

def pga(raw_lines):
    """
    This main function combines above helper functions to create log analysis
    """

    game = build_game_log(raw_lines)
    log = game['log']
    players = game['players']

    current_company = {company:{'tiles':set(), 'size':0, 'price':0, 'available':25} for company in companies}
    current_scoreboard = {player:{'Net':6000, 'Cash':6000, 'stock_value':0, 'bonus_value':0} for player in players}
    scoreboard = {0:copy.deepcopy(current_scoreboard)}
    unused_tiles = log[1]['tiles_played'] - {log[1]['tile_played']}

    for i in range(1, len(log), 1):
        
        ### Handle chain sizes
        new_tile = log[i]['tile_played']
        #print()
        #print()
        #print('BEGIN TURN:', i, 'NEW TILE', new_tile)
        # Keep record of company share prices
        temp_co_share_prices = {}
        for co in companies:
            temp_co_share_prices[co]=current_company[co]['price']
        
        # New company
        if log[i]['is_founding']:
            # Find new company
            for line in log[i]['text']:
                if 'formed ' in line:          
                    new_company = line.replace('.', '').split(' ')[-1]

            # Add starting piece to current company:
            current_company[new_company]['tiles'].add(new_tile)
        
        # Merger
        elif log[i]['is_merger']:
            # Add piece to merger survivor
            survivor = log[i]['merger_survivor']
            current_company[survivor]['tiles'].add(new_tile)
            
            # Move pieces from companies lost in merger:
            for company_lost in log[i]['merger_lost']:
                #print('COMPANY LOST TO MERGER:', company_lost)
                for tile_moved in current_company[company_lost]['tiles']:
                    current_company[survivor]['tiles'].add(tile_moved)
                current_company[company_lost]['tiles'] = set()
            #print('COMPANIES AFTER MERGER', current_company)
            
        
        # Add tile to unused
        else:
            unused_tiles.add(new_tile)

        # Check all unused tiles
        # Recursion depth of 4 should be more than enough to bring in a chain of other tiles
        nMax = 4
        nIdx = 1
        while nIdx <= nMax:
            temp_unused_tiles = copy.deepcopy(unused_tiles)
            for tile in temp_unused_tiles:
                for company in companies:
                    temp_company_tiles = copy.deepcopy(current_company[company]['tiles'])
                    for company_tile in temp_company_tiles:
                        if is_adjacent(tile, company_tile) and tile in unused_tiles:
                            current_company[company]['tiles'].add(tile)
                            unused_tiles.remove(tile)
            nIdx += 1


        ### Update chain sizes, cost & available shares
        for co in companies:
            current_company[co]['size'] = len(current_company[co]['tiles'])
            shares_taken = 0
            for player in players:
                shares_taken += log[i]['shares'][player][co]
            current_company[co]['available'] = 25 - shares_taken
            company_size = current_company[co]['size']
            if company_size <= 5:
                co_price = company_size*100
            elif company_size <= 10:
                co_price = 600
            elif company_size <= 20:
                co_price = 700
            elif company_size <= 30:
                co_price = 800
            elif company_size <= 40:
                co_price = 900
            else:
                co_price = 1000

            if company_size > 0:
                if co == 'Worldwide' or co == 'American' or co == 'Festival':
                    co_price += 100
                elif co == 'Imperial' or co == 'Continental':
                    co_price += 200

            current_company[co]['price'] = co_price

        log[i]['current_company'] = copy.deepcopy(current_company)


        ### UPDATE CURRENT SCOREBOARD

        ### Update player stock value
        for player in players:
            stock_value = 0
            for co in companies:
                stocks = log[i]['shares'][player][co]
                stock_price = current_company[co]['price']
                stock_value += stocks*stock_price
            current_scoreboard[player]['stock_value'] = stock_value

        ### Update player bonus value
        # Reset
        for player in players:
            current_scoreboard[player]['bonus_value'] = 0
            
        for co in companies:
            if current_company[co]['price'] != 0:
                majority_bonus = current_company[co]['price'] * 10
                minority_bonus = current_company[co]['price'] * 5
                player_stocks = {player:log[i]['shares'][player][co] for player in players}

                max_stocks = max(player_stocks.values())
                majority_shareholders = {key for key, value in player_stocks.items() if value == max_stocks}
                if len(majority_shareholders) > 1:
                    for player in majority_shareholders:
                        current_scoreboard[player]['bonus_value'] += int(math.ceil((majority_bonus + minority_bonus)/len(majority_shareholders) / 100.0)) * 100
                else:
                    majority_shareholder = majority_shareholders.pop()
                    current_scoreboard[majority_shareholder]['bonus_value'] += majority_bonus

                    player_stocks[majority_shareholder] = -99
                    max_stocks = max(player_stocks.values())
                    minority_shareholders = {key for key, value in player_stocks.items() if value == max_stocks}
                    for player in minority_shareholders:
                        current_scoreboard[player]['bonus_value'] += int(math.ceil(minority_bonus/len(minority_shareholders) / 100.0)) * 100

            

        ### Update player cash
        # Purchased shares
        player = log[i]['player']
        purchased_shares = log[i]['purchased_shares']
        for co in purchased_shares.keys():
            cost = current_company[co]['price']
            current_scoreboard[player]['Cash'] -= cost*purchased_shares[co]

        # Bonuses
        for player in log[i]['bonus_paid'].keys():
            current_scoreboard[player]['Cash'] += log[i]['bonus_paid'][player]


        # Sold shares:
        #print('SCOREBOARD BEFORE:')
        #pprint.pprint(current_scoreboard)
        for transaction in log[i]['sold_shares']:
            #print('SOLD SHARES', log[i]['sold_shares'])

            player = transaction[0]
            co = transaction[1]
            qty = transaction[2]
            price = temp_co_share_prices[co]
            current_scoreboard[player]['Cash'] += qty*price
        #print('SCOREBOARD AFTER:')
        #pprint.pprint(current_scoreboard)

        ### Update player net worth
        for player in players:
            current_scoreboard[player]['Net'] = sum([
                current_scoreboard[player]['Cash'],
                current_scoreboard[player]['stock_value'],
                current_scoreboard[player]['bonus_value']])

        ### Add current turn's scoreboard to log
        scoreboard[i] = copy.deepcopy(current_scoreboard)
            
    return( {'log':log, 'players': players, 'scoreboard':scoreboard} )


result = pga(raw_lines)
log = result['log']
players = result['players']
scoreboard = result['scoreboard']


#print(companies)
#print([len(current_company[x]['tiles']) for x in companies])
#print(sum([len(current_company[x]['tiles']) for x in companies], len(unused_tiles)))

# Convert scorecard to turn by turn DataFrame:
def plot_game_summary(scoreboard, players):
    temp = {}
    for firstcol in ['Net', 'Cash', 'stock_value', 'bonus_value']:
        for secondcol in players:
            temp[(firstcol, secondcol)] = {i:scoreboard[i][secondcol][firstcol] for i in range(len(scoreboard))}
    df1 = pd.DataFrame(temp)
    df1.plot(y='Net', kind = 'line', title='Net Worth by Turn')
    df1.plot(y='Cash', kind = 'line', title='Cash by Turn')
    df1.plot(y='stock_value', kind = 'line', title='Stock Value by Turn')
    #df1.plot(y='bonus_value', kind = 'line', title='Bonus Value by Turn')
    pylab.show()


def plot_player_summary(scoreboard, players):
    temp = {}
    for firstcol in players:
        for secondcol in ['Net', 'Cash', 'stock_value', 'bonus_value']:
            temp[(firstcol, secondcol)] = {i:scoreboard[i][firstcol][secondcol] for i in range(len(scoreboard))}
    df2 = pd.DataFrame(temp)
    # Set ylim to round up to nearest multiple of 5,000
    yMax = math.ceil(max([scoreboard[len(scoreboard)-1][player]['Net'] for player in players])/5000)*5000
    for player in players:
        df2[player].drop(['Net'], axis = 1).plot(kind = 'area', title=player).set_ylim(0,yMax)
    pylab.show()


