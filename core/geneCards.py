"""This file should not be used other than generating the card infos. """

import json
import io

# Store the clues card info
class Card:
    def __init__(self, name_en, name_tw = '', url = ''):
        self.name_en = name_en
        self.name_tw = name_tw
        self.url = url

card_detail = []
weapon_detail = []

f = open('raw_clues.txt', 'r', encoding='utf-8')
line = f.readline()
while line:
    tmp_name_en = line[:-1]
    tmp_name_tw = f.readline()[:-1]
    tmp_url = f.readline()[:-1]
    line = f.readline()

    new_clue = Card(tmp_name_en, tmp_name_tw, tmp_url).__dict__
    card_detail.append(new_clue)
f.close()

f = open('raw_weapon.txt', 'r', encoding='utf-8')
line = f.readline()
while line:
    tmp_name_en = line[:-1]
    tmp_name_tw = f.readline()[:-1]
    tmp_url = f.readline()[:-1]
    line = f.readline()

    new_weapon = Card(tmp_name_en, tmp_name_tw, tmp_url).__dict__
    weapon_detail.append(new_weapon)
f.close()


with open('cards.json', 'w') as f:
    store_data = {}
    store_data['Clues'] = card_detail
    store_data['Weapons'] = weapon_detail
    json.dump(store_data, f, indent=4, sort_keys=True)

################################
#         Testing Area         #

with open('cards.json', 'r') as f:
    store_data = json.load(f)
    for c in store_data['Clues']:
        #print(f"Read card name = {c.name_en}")
        #print(f"卡片名稱 = {c.name_tw}")
        print(f"What i get is : {c['name_tw']}")
    for w in store_data['Weapons']:
        print(f"What i get is : {w['name_en']}")