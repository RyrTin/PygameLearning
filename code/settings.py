# 作   者：许晨昊
# 开发日期：9/3/2023
from pygame.math import Vector2

# 存放各种基本静态参数
# 屏幕尺寸
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

# 覆盖层位置
OVERLAY_POSITIONS = {
    'tool': (40, SCREEN_HEIGHT - 15),
    'seed': (70, SCREEN_HEIGHT - 5),
    'map': (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 500),
    'info': (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 470),
    'health': (40, 30),
    'magic': (40, 60)
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
    'wood': 4,
    'apple': 2,
    'corn': 10,
    'tomato': 20
}

# 购买价格
PURCHASE_PRICES = {
    'corn': 4,
    'tomato': 5
}

# 开始界面
START_MENU = {
    'start': '开始',
    'setting': '设置'
}
