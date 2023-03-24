# 作   者：许晨昊
# 开发日期：24/3/2023

import pygame
from settings import *


class Menu:
    def __init__(self, player, toggle_menu):
        # 基本设置
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)


