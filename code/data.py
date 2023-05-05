# 作   者：许晨昊
# 开发日期：9/3/2023
from pygame.math import Vector2

# 存放各种基本静态参数
# 屏幕尺寸
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64
# 帧数
FPS = 60

# 覆盖层位置
OVERLAY_POSITIONS = {
    'tool': (40, SCREEN_HEIGHT - 15),
    'seed': (70, SCREEN_HEIGHT - 5),
    'map': (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 500),
    'info': (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 470),
    'health': (40, 30),
    'magic': (40, 60),
    'atk': (40, 90),
    'atk_n': (80, 90),
    'mag': (150, 90),
    'mag_n': (190, 90),
    'money': (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 440)
}

# 工具位移
PLAYER_TOOL_OFFSET = {
    'left': Vector2(-50, 40),
    'right': Vector2(50, 40),
    'up': Vector2(0, -10),
    'down': Vector2(0, 50)
}

# 图层优先级
LAYERS = {
    'water': 0,
    'ground': 1,
    'soil': 2,
    'soil water': 3,
    'rain floor': 4,
    'house bottom': 5,
    'ground plant': 6,
    'main': 7,
    'house top': 8,
    'fruit': 9,
    'rain drops': 10
}

# 苹果刷新位置
APPLE_POS = {
    'Small': [(18, 17), (30, 37), (12, 50), (30, 45), (20, 30), (30, 10)],
    'Large': [(30, 24), (60, 65), (50, 50), (16, 40), (45, 50), (42, 70)]
}

# 作物生长速度
GROW_SPEED = {
    'corn': 1,
    'tomato': 0.7
}

# 出售售价
SALE_PRICES = {
    'wood': 10,
    'apple': 5,
}

# 购买价格
PURCHASE_PRICES = {
    'health': 50,
    'energy': 50,
    'attack': 1,
    'magic': 1,
}

# 开始界面
START_MENU = {
    'start': '开始',
    'setting': '设置'
}

# 碰撞盒位移
HITBOX_OFFSET = {
    'player': (-126, -80),
    'object': -50,
    'grass': -10,
    'invisible': 0}

# UI设置
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = '../font/LycheeSoda.ttf'
UI_FONT_SIZE = 20

# 基本颜色
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# UI颜色
HEALTH_COLOR = 'Pink'
ENERGY_COLOR = 'Blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# 设置格式
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
BG_COLOR_SELECTED = '#EEEEEE'

# 武器数据
weapon_data = {'GM_sword': {
    'cooldown': 200, 'damage': 9999, 'graphic': '../graphics/weapons/GM_sword/full.png'},
    'sword': {'cooldown': 300, 'damage': 15, 'graphic': '../graphics/weapons/sword/full.png'},
    'lance': {'cooldown': 600, 'damage': 30, 'graphic': '../graphics/weapons/lance/full.png'},
    'axe': {'cooldown': 500, 'damage': 25, 'graphic': '../graphics/weapons/axe/full.png'},
    'rapier': {'cooldown': 150, 'damage': 8, 'graphic': '../graphics/weapons/rapier/full.png'},
    'sai': {'cooldown': 120, 'damage': 10, 'graphic': '../graphics/weapons/sai/full.png'}}

# 技能数据
magic_data = {
    'flame': {'strength': 5, 'cost': 20, 'graphic': '../graphics/particles/flame/fire.png'},
    'heal': {'strength': 20, 'cost': 30, 'graphic': '../graphics/particles/heal/heal.png'}}

# 敌人数据
monster_data = {
    'squid': {'health': 100, 'money': 8, 'damage': 18, 'attack_type': 'slash',
              'attack_sound': '../audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 80,
              'notice_radius': 360},
    'raccoon': {'health': 300, 'money': 15, 'damage': 40, 'attack_type': 'claw',
                'attack_sound': '../audio/attack/claw.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 130,
                'notice_radius': 400},
    'spirit': {'health': 100, 'money': 5, 'damage': 12, 'attack_type': 'thunder',
               'attack_sound': '../audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 60,
               'notice_radius': 350},
    'bamboo': {'health': 70, 'money': 3, 'damage': 8, 'attack_type': 'leaf_attack',
               'attack_sound': '../audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 50,
               'notice_radius': 300}}
# 仓库
item_inventory = {
            'wood': 5,
            'apple': 5,
            'corn': 5,
            'tomato': 5}

# 种子库存
seed_inventory = {
            'corn': 2,
            'tomato': 3}

# 音量
volumes = {'bgm': 0.4, 'action': 0.2, 'item': 0.1}
max_volume = {'bgm': 0.8, 'action': 0.4, 'item': 0.4}
min_volume = 0

# 收入
rewards = {'fight': 0}

# 玩家属性
player_stats = {'health': 100, 'energy': 60, 'attack': 0, 'magic': 0, 'speed': 5}
player_max_stats = {'health': 200, 'energy': 140, 'attack': 20, 'magic': 20, 'speed': 10}
