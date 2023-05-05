# 作   者：许晨昊
# 开发日期：2023/5/5
import random

weapon_data = {'GM_sword': {
    'cooldown': 10, 'damage': 9999, 'graphic': '../graphics/weapons/GM_sword/full.png'},
    'sword': {'cooldown': 100, 'damage': 15, 'graphic': '../graphics/weapons/sword/full.png'},
    'lance': {'cooldown': 400, 'damage': 30, 'graphic': '../graphics/weapons/lance/full.png'},
    'axe': {'cooldown': 300, 'damage': 20, 'graphic': '../graphics/weapons/axe/full.png'},
    'rapier': {'cooldown': 50, 'damage': 8, 'graphic': '../graphics/weapons/rapier/full.png'},
    'sai': {'cooldown': 80, 'damage': 10, 'graphic': '../graphics/weapons/sai/full.png'}}

print(random.sample(weapon_data.keys(), 2))
