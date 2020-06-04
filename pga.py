#Read Acquire log file
with open('C:\\4. Github\\PGA\\log1.txt') as f:
    lines = f.read().splitlines()

def pga(lines):
    """
    Run analyses for Acquire logs
    """
    ### Establish lists for gameplay, scoreboard & players
    gameplay = []
    nInclude = 0
    for line in lines:
        if 'played tile ' in line:
            nInclude = 1
        elif 'Game over' in line:
            nInclude = 0
        if nInclude == 1:
            gameplay.append(line)

    scoreboard = []
    for line in lines:
        if  line.startswith('Player'):
            nInclude = 1
        elif 'Price ($00)' in line:
            nInclude = 0
        if nInclude == 1:
            scoreboard.append(line)

    players = []
    for line in scoreboard[1:-2]:
        # Scoreboard lines can be separated by tab or space. Handle either way
        if '\t' in line:
            player = line.split('\t')[0]
        else:
            player = line.split(' ')[0]
        players.append(player)

    ### Loop through scoreboard
    final_net_worth = {player:0 for player in players}
    for line in scoreboard[1:-2]:
        # Scoreboard lines can be separated by tab or space. Handle either way
        if '\t' in line:
            splt = line.split('\t')
        else:
            splt = line.split(' ')
        final_net_worth[splt[0]] = splt[-1]


    ### Loop through gameplay
    companies_formed = {player:0 for player in players}
    bonus_money = {player:0 for player in players} 
    merging_tiles = {player:0 for player in players}

    for line in gameplay:
        if 'formed ' in line:
            companies_formed[line.split(' ')[0]] += 1
            
        if 'received a $' in line:
            amt = int(''.join(filter(str.isdigit, line)))
            bonus_money[line.split(' ')[0]] += amt

        if ' merged ' in line:
            merging_tiles[line.split(' ')[0]] += 1


    ### Print output. Someday this could be fancier :)        
    print("Companies Formed:")
    print(companies_formed)
    print()

    print("Bonus Money:")
    print(bonus_money)
    print()

    print("Final net worth:")
    print(final_net_worth)
    print()

    print("Merging Tiles Played:")
    print(merging_tiles)
    print()

pga(lines)
    

