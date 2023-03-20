# 作   者：许晨昊
# 开发日期：15/3/2023
import pygame

from settings import *


# 覆盖层类似于UI的功能，并且相对于其他元素，这里的东西都固定在屏幕上
class Overlay:
    def __init__(self, player):
        # 初始设置 导入player
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # 导入覆盖层（图标）的图片路径
        overlay_path = '../graphics/overlay/'
        # 建立工具图像字典
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha()
                           for tool in player.tools}
        # 建立种子图像字典
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha()
                           for seed in player.seeds}
        # 生成小地图
        self.map_surf_pre = pygame.image.load('../graphics/world/map.png').convert_alpha()
        self.map_surf = pygame.transform.scale(self.map_surf_old, (200, 200))

        # 生成人物头像
        self.figure_surf_pre = pygame.image.load('../graphics/objects/')

    def display(self):
        # 显示工具图标
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)

        # 显示种子图标
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf, seed_rect)

        # 显示地图
        map_surf = self.map_surf
        map_rect = map_surf.get_rect(midbottom=OVERLAY_POSITIONS['map'])
        self.display_surface.blit(map_surf, map_rect)
        pygame.draw.rect(self.display_surface, 'black', map_rect, 5)
