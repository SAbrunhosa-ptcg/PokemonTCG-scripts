import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

### CLASSES ###

# class to hold individual player information
class Player:
    def __init__(self, player_id, name, link, classification):
        self.id = player_id # unique ID, in case it is useful later (not pokemonID)
        self.name = name
        
        self.decklist_link = link
        self.classification = classification
        self.CP = 0
        self.Day2 = False
        
        self.decklist = []
        self.pokemonlist = []
        self.archetype = 'Lost Box'
        self.variant = 'Lost Kyogre' # RIP

    def calculateCP(self):
        # need to add kicker check to make this transversal to all tournament sizes
        max_rank = 512
        if self.classification > max_rank:
            self.CP = 0
        elif self.classification > 512:
            self.CP = 20
        elif self.classification > 256:
            self.CP = 40
        elif self.classification > 128:
            self.CP = 60
        elif self.classification > 64:
            self.CP = 80
        elif self.classification > 32:
            self.CP = 100
        elif self.classification > 16:
            self.CP = 125
        elif self.classification > 8:
            self.CP = 160
        elif self.classification > 4:
            self.CP = 280
        elif self.classification > 2:
            self.CP = 300
        elif self.classification > 1:
            self.CP = 325
        elif self.classification > 0:
            self.CP = 350
        else:
            # the rk9 table has some players with empty classification
            print("That is a strange classification you got there. Name: " + str(self.name))
            self.CP = 0

    def checkDay2(self, limit):
        if self.classification < limit and self.classification > 0:
            self.Day2 = True
        else:
            self.Day2 = False

### FUNCTIONS ###

# get decklist from URL
def GetDecklist(URL):
    soup_player = GetWebpage(URL)
    find_list = soup_player.find_all('li', attrs={'data-language': "EN"}) # find all HTML list 'li' elements with EN cards
    #print(find_list)

    card_list = [] # list to hold all cards inside a given player's decklist
    
    for element in find_list:
        card_list.append([element['class'][0], element['data-cardname'], element['data-quantity'], element['data-setnum']])

    #print(card_list)
    
    return card_list

# get pokemon list from decklist
def GetPokemonList(decklist):
    pokemon_list = [] # list to hold all pokemon inside a given player's decklist
    
    for element in decklist:
        #print(element)
        if element[0] == 'pokemon':
            if element[1] not in pokemon_list:
                pokemon_list.append(element[1])

    #print(pokemon_list)
    
    return pokemon_list

# get soup from URL
def GetWebpage(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

# scrap tournament data
def GetPlayerData(tournament_soup):  
    find_list = tournament_soup.find_all('tr') # get all players from the player table (i.e. table rows)
    find_list.pop(0) # pop header row
    
    # counters for number of players in each division
    master_counter = 0
    senior_counter = 0 
    junior_counter = 0
    
    # list for Masters players
    player_list = []
    
    for i in range(len(find_list)): # loop through players (i.e. table rows)
        player_info = find_list[i].find_all('td') # get player data from the row (i.e. table element)
        
        # check player division
        if 'Masters' in player_info[4]:
            master_counter += 1
        elif 'Senior' in player_info[4]:
            senior_counter += 1
            continue
        elif 'Junior' in player_info[4]:
            junior_counter += 1
            continue
    
        # continue gathering information for Masters players only
        player_name = player_info[1].text + " " + player_info[2].text.strip()
        player_link = player_info[5].find_all('a')[0]['href']
        try: 
            player_classification = int(player_info[6].text)
        except:
            print('Error retrieving player classification for: ' + player_name)
            player_classification = -1 # -1 will be used for some checks in the code later
    
        #print(player_name)
        #print(player_link)
        #print(player_classification)
    
        player_list.append(Player(i, player_name, player_link, player_classification))

    return player_list, master_counter, senior_counter, junior_counter

# Get archetype and variant from decklist
def GetArchetype(pokemonList):     
    # Parse through the deck possibilities (updated: 13/02/2025)
    # Deck variant to be implemented later (just '' for now)
    if 'Charizard ex' in pokemonList and 'Terapagos ex' not in pokemonList and 'Dragapult ex' not in pokemonList:
        #print("Found a Zard player!")
        return 'Charizard (no Dragapult)', ''
  
    elif 'Roaring Moon' in pokemonList and 'Roaring Moon ex' not in pokemonList:
        return 'Ancient Box', ''
    
    elif 'Archaludon ex' in pokemonList and 'Origin Forme Dialga VSTAR' in pokemonList:
        return 'Archaludon ex Dialga', ''

    elif 'Archaludon ex' in pokemonList and 'Origin Forme Dialga VSTAR' not in pokemonList:
        return 'Archaludon ex (no Dialga)', ''
    
    elif 'Ceruledge ex' in pokemonList:
        return 'Ceruledge ex', ''
    
    elif 'Regidrago VSTAR' in pokemonList and 'Teal Mask Ogerpon ex' in pokemonList:
        return 'Regidrago VSTAR', ''
    
    elif 'Dragapult ex' in pokemonList and 'Dusknoir' in pokemonList and 'Pidgeot ex' not in pokemonList:
        return 'Dragapult Dusknoir (no Pidgeot)', ''
    
    elif 'Dragapult ex' in pokemonList and 'Pidgeot ex' in pokemonList:
        return 'Dragapult (Other)', ''
    
    elif 'Dragapult ex' in pokemonList and 'Iron Thorns ex' in pokemonList:
        return 'Dragapult Iron Thorns', ''
    
    elif 'Dragapult ex' in pokemonList and 'Charizard ex' in pokemonList:
        return 'DragaZard ex', ''

    elif 'Dragapult ex' in pokemonList:
        return 'Dragapult (Other)', ''
    
    elif 'Gardevoir ex' and ('Scream Tail' in pokemonList or 'Drifloon' in pokemonList):
        return 'Gardevoir ex', ''
    
    elif 'Terapagos ex' and 'Brute Bonnet' in pokemonList:
        return 'Poison Terapagos', ''
    
    elif 'Comfey' in pokemonList and ('Cramorant' in pokemonList or 'Sableye' in pokemonList):
        return 'Lost Zone Box', ''
    
    elif 'Roaring Moon ex' in pokemonList:
        return 'Roaring Moon ex', ''
    
    elif 'Pidgeot ex' in pokemonList and ('Wellspring Mask Ogerpon ex' in pokemonList or 'Luxray V' in pokemonList):
        return 'Pidgeot Control', ''
    
    elif 'Snorlax' in pokemonList:
        return 'Snorlax Stall', ''
    
    elif 'Lugia VSTAR' in pokemonList and 'Cinccino' in pokemonList:
        return 'Lugia (Cinccino)', ''

    elif 'Lugia VSTAR' in pokemonList and 'Cinccino' not in pokemonList:
        return 'Lugia (no Cinccino)', ''
    
    elif 'Gholdengo ex' in pokemonList:
        return 'Gholdengo ex', ''
    
    elif 'Miraidon ex' in pokemonList:
        return 'Miraidon ex', ''
    
    elif 'Raging Bolt ex' in pokemonList:
        return 'Raging Bolt', ''

    elif 'Gouging Fire ex' in pokemonList and 'Arceus VSTAR' not in pokemonList:
        return 'Gouging Fire', ''

    # 'Wall' stands for Milotic, Cornerstone Ogerpon, Mimikyu, etc.
    elif 'Milotic ex' in pokemonList or 'Cornerstone Mask Ogerpon ex' in pokemonList:
        return 'Wall', ''

    elif 'Iron Thorns ex' in pokemonList:
        return 'Quad Thorns', ''
    
    elif 'Terapagos ex' in pokemonList and 'Dusknoir' in pokemonList:
        return 'Terapagos Dusknoir', ''
    
    elif 'Origin Forme Palkia VSTAR' in pokemonList:
        return 'Palkia', ''
    
    return 'Other', ''

def ExportData(player_list, filename):
    data_list = []
    for player in player_list:
        temp = [player.id, player.name, player.decklist_link, player.classification, player.CP, player.Day2,\
                player.decklist, player.pokemonlist, player.archetype, player.variant]
        data_list.append(temp)
    
    dataframe = pd.DataFrame(data_list, columns=['ID', 'Name', 'Link', 'Classification', 'CP', 'Day 2',\
                                                 'Decklist', 'Pokemon List', 'Archetype', 'Variant'])
    dataframe.to_excel(filename)
    
def ImportData(filename):
    # could use some cleaning, especially for data types, but I am too lazy for now
    imported_data = pd.read_excel(filename)
    imported_data = imported_data.values.tolist()
    
    imported_players = []
    for player in imported_data:
        # __init__(self, player_id, name, link, classification)
        new_player = Player(int(player[1]), player[2], player[3], int(player[4]))
        new_player.CP = int(player[5])
        new_player.Day2 = bool(player[6])
        new_player.decklist = np.array(eval(player[7])).tolist()
        new_player.pokemonlist = np.array(eval(player[8])).tolist()
        new_player.archetype = player[9]
        new_player.variant = player[10]
        imported_players.append(new_player)
    return imported_players