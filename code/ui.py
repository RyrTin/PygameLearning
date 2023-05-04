import pygame
from settings import *


class UI:
    def __init__(self):

        # 基本设置
        self.energy_bar_rect = None
        self.health_bar_rect = None
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.font_b = pygame.font.Font(UI_FONT, UI_FONT_SIZE + 10)

        # 添加武器目录
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)

        # 添加魔法目录
        self.magic_graphics = []
        for magic in magic_data.values():
            magic = pygame.image.load(magic['graphic']).convert_alpha()
            self.magic_graphics.append(magic)

    def show_bar(self, current, max_amount, bg_rect, color):
        # 绘制状态条
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect, 0, 6)

        # 计算状态值百分比
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # 填充状态值
        pygame.draw.rect(self.display_surface, color, current_rect, 0, 6)
        # 填充边框
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 2, 6)

    # 显示金钱
    def show_money(self, money):
        text_surf = self.font.render(str(int(money)), False, TEXT_COLOR)
        x = self.display_surface.get_size()[0] - 20
        y = self.display_surface.get_size()[1] - 20
        text_rect = text_surf.get_rect(bottomright=(x, y))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

    # 高亮选择条
    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect

    # 武器显示
    def weapon_overlay(self, weapon_index, has_switched):
        bg_rect = self.selection_box(10, 630, has_switched)
        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(weapon_surf, weapon_rect)

    # 魔法显示
    def magic_overlay(self, magic_index, has_switched):
        bg_rect = self.selection_box(80, 635, has_switched)
        magic_surf = self.magic_graphics[magic_index]
        magic_rect = magic_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(magic_surf, magic_rect)

    def show_text(self, player):
        hp_surf = self.font.render(f'HP', False, 'Black')
        hp_rect = hp_surf.get_rect(topleft=OVERLAY_POSITIONS['health'])
        self.display_surface.blit(hp_surf, hp_rect)
        mp_surf = self.font.render(f'MP', False, 'Black')
        mp_rect = mp_surf.get_rect(topleft=OVERLAY_POSITIONS['magic'])
        self.display_surface.blit(mp_surf, mp_rect)
        atk_surf = self.font.render(f'ATK', False, 'Gold')
        atk_rect = mp_surf.get_rect(topleft=OVERLAY_POSITIONS['atk'])
        self.display_surface.blit(atk_surf, atk_rect)

        atk_n = str(player.get_full_weapon_damage())
        atk_n_surf = self.font_b.render(atk_n, False, 'Gold')
        atk_n_rect = mp_surf.get_rect(topleft=OVERLAY_POSITIONS['atk_n'])
        self.display_surface.blit(atk_n_surf, atk_n_rect)

    # 更新UI条
    def display(self, player):

        # 状态栏设置
        self.health_bar_rect = pygame.Rect(70, 30, player.stats['health'] * 3, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(70, 60, player.stats['energy'] * 3, BAR_HEIGHT)
        # 显示文字
        self.show_text(player)
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
        # 显示金币
        self.show_money(player.money)

        # 显示武器栏、法术栏
        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon)
        self.magic_overlay(player.magic_index, not player.can_switch_magic)
