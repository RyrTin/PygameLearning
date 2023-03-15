# 作   者：许晨昊
# 开发日期：15/3/2023
import pygame

from settings import *


class Overlay:
    def __init__(self, player):
        # 初始设置 导入player
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # 导入覆盖层（图标）的图片路径
        overlay_path = '../graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha()
                           for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha()
                           for seed in player.seeds}
        print(self.tools_surf)
        print(self.seeds_surf)

    def display(self):

        # 显示现在用的工具是什么
        tool_surf = self.tools_surf[self.player.selected_tool]
        self.display_surface.blit(tool_surf, (0, 0))
