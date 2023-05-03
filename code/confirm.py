# 作   者：许晨昊
# 开发日期：2023/5/1

import pygame
from data import *


class Confirm:
    def __init__(self, player):

        # 基本设置
        self.player = player
        self.item_list = []
        # 获取显示区
        self.display_surface = pygame.display.get_surface()

        # 属性条设置
        self.attribute_nr = 2
        self.attribute_names = ('yes', 'no')
        self.font = pygame.font.Font(UI_FONT, 40)

        # 属性条高度
        # 获得高度
        self.height = self.display_surface.get_size()[1] // 10
        # 获得宽度
        self.width = self.display_surface.get_size()[0] // 6
        self.create_items()

        # 选择属性
        # 选中标签
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_move:
            # 左右移动选择属性
            # 防止越界
            if keys[pygame.K_d] and self.selection_index < self.attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_a] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            # 触发效果
            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

                if self.selection_index == 0:
                    self.player.game_paused = False
                    self.player.quit = True
                if self.selection_index == 1:
                    self.player.game_paused = False

    # 控制选择速度（不然太快了）
    def selection_cooldown(self):
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            # 自动恢复冷却时间（否则无法按下下一个按键）
            if current_time - self.selection_time >= 300:
                self.can_move = True

    # 创建选项图像
    def create_items(self):

        for item, index in enumerate(range(self.attribute_nr)):
            # 控制水平位置
            # 获得显示区全宽

            full_width = self.display_surface.get_size()[0]
            left = (index+1)*(full_width//3) - 100

            # 每一条属性的顶边位置
            top = self.display_surface.get_size()[1] * 0.4

            # 创建显示条加入列表
            item = Item(left, top, self.width, self.height, index, self.font)
            self.item_list.append(item)

    def display(self):
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            # 获得属性
            # 迭代到这个属性 就把他对应的框、条和字显示出来
            # bgm action item
            name = self.attribute_names[index]
            # 这三个对应的值
            item.display(self.display_surface, self.selection_index, name)


class Item:
    def __init__(self, l, t, w, h, index, font):
        # 选项初始属性
        self.move = None
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font

    # 显示选项名称
    def display_names(self, surface, name, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        # 获得属性名称图像
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        # 绘制表格
        surface.blit(title_surf, title_rect)

    def display(self, surface, selection_num, name):
        # 绘制选中框
        if self.index == selection_num:
            # 选中框的颜色与其他的不同
            pygame.draw.rect(surface, BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, self.index == selection_num)
