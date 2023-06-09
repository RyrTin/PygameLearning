# 作   者：许晨昊
# 开发日期：15/3/2023
import pygame

from data import *
from time import strftime
from time import gmtime
import math


# 覆盖层类似于UI的功能，并且相对于其他元素，这里的东西都固定在屏幕上
class Overlay:
    def __init__(self, player):

        # 初始设置 导入player
        self.time = None
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.font_n = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        self.font_w = pygame.font.Font('../font/LycheeSoda.ttf', 20)
        self.font_b = pygame.font.Font('../font/LycheeSoda.ttf', 40)

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
        self.map_surf = pygame.transform.scale(self.map_surf_pre, (200, 200))

        # 生成人物头像
        self.figure_surf_pre = pygame.image.load('../graphics/objects/figure.png').convert_alpha()
        self.figure_surf = pygame.transform.scale(self.figure_surf_pre, (40, 30))
        self.figure_x = SCREEN_WIDTH - 120
        self.figure_y = SCREEN_HEIGHT - 550

    def display_tip(self):
        title_surf = self.font_b.render('Q', False, 'White')
        title_rect = title_surf.get_rect(topleft=(42, SCREEN_HEIGHT - 120))
        self.display_surface.blit(title_surf, title_rect)

        title_surf = self.font_b.render('E', False, 'White')
        title_rect = title_surf.get_rect(topleft=(92, SCREEN_HEIGHT - 102))
        self.display_surface.blit(title_surf, title_rect)

    def display_seed(self, player):
        title_surf = self.font_n.render('you have ' + str(seed_inventory[player.selected_seed]), False, 'White')
        title_rect = title_surf.get_rect(topleft=(100, SCREEN_HEIGHT - 40))
        self.display_surface.blit(title_surf, title_rect)

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

        # 显示头像
        self.figure_x += self.player.get_move_x() / 15
        self.figure_y += self.player.get_move_y() / 15
        figure_surf = self.figure_surf
        figure_rect = figure_surf.get_rect(midbottom=(self.figure_x, self.figure_y))
        self.display_surface.blit(figure_surf, figure_rect)

        # 显示时间
        # 将秒转化为时分秒
        self.time = strftime("%H:%M:%S", gmtime(480 + math.floor(self.player.timers['time'].pass_time() / 1000)))
        self.time = self.time.split(':')[1] + ':' + self.time.split(':')[2]

        time_surf = self.font_n.render(f'{self.time}', False, 'Black')
        time_rect = time_surf.get_rect(midbottom=OVERLAY_POSITIONS['info'])
        self.display_surface.blit(time_surf, time_rect)

        # 显示状态
        # rect的参数为（区域，颜色，（（左，顶），（宽，高）），边框宽度，弧度）
        health_rect = (70, 30, player_stats['health'] * 3, 20)
        magic_rect = (70, 60, player_stats['energy'] * 3, 20)
        pygame.draw.rect(self.display_surface, 'Pink', health_rect, 0, 6)
        pygame.draw.rect(self.display_surface, 'Blue', magic_rect, 0, 6)
        pygame.draw.rect(self.display_surface, 'Black', health_rect, 2, 6)
        pygame.draw.rect(self.display_surface, 'Black', magic_rect, 2, 6)

        # 显示文本
        hp_text = self.font_w.render(str(player_stats['health']) + '/' + str(player_stats['health']), False, 'White')
        hp_text_rect = hp_text.get_rect(topleft=(80 + player_stats['health'] * 3, 30))
        self.display_surface.blit(hp_text, hp_text_rect)

        hp_surf = self.font_w.render(f'HP', False, 'Black')
        hp_rect = hp_surf.get_rect(topleft=OVERLAY_POSITIONS['health'])
        self.display_surface.blit(hp_surf, hp_rect)

        mp_text = self.font_w.render(str(player_stats['energy']) + '/' + str(player_stats['energy']), False, 'White')
        mp_text_rect = hp_text.get_rect(topleft=(80 + player_stats['energy'] * 3, 60))
        self.display_surface.blit(mp_text, mp_text_rect)

        mp_surf = self.font_w.render(f'MP', False, 'Black')
        mp_rect = mp_surf.get_rect(topleft=OVERLAY_POSITIONS['magic'])
        self.display_surface.blit(mp_surf, mp_rect)

        # 显示money
        text_surf = self.font_n.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom=OVERLAY_POSITIONS['money'])

        self.display_surface.blit(text_surf, text_rect)
        self.display_tip()
        self.display_seed(self.player)