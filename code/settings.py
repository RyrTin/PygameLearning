# 作   者：许晨昊
# 开发日期：17/4/2023

import pygame
from data import *


class Settings:
    def __init__(self):

        # 基本设置

        self.item_list = []
        # 获取显示区
        self.display_surface = pygame.display.get_surface()

        # 属性条设置
        self.attribute_nr = len(volumes)
        self.attribute_names = list(volumes.keys())
        self.max_values = list(max_volume.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # 属性条高度
        # 获得高度
        self.height = self.display_surface.get_size()[1] * 0.8
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
            if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            # 触发效果
            if keys[pygame.K_UP]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].trigger(0.1)
            elif keys[pygame.K_DOWN]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].trigger(-0.1)

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
            # 每条的平均宽度
            increment = full_width // self.attribute_nr
            # 每一条的左边条位置
            # 通过控制self.width的宽度来控制整体宽度
            left = (item * increment) + (increment - self.width) // 2

            # 每一条属性的顶边位置
            top = self.display_surface.get_size()[1] * 0.1

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
            value = volumes[name]
            max_value = self.max_values[index]
            item.display(self.display_surface, self.selection_index, name, value, max_value)


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

        # 获得属性当前值
        value_surf = self.font.render(f'{round((volumes[name]), 1)}', False, color)
        value_rect = value_surf.get_rect(midbottom=self.rect.midbottom - pygame.math.Vector2(0, 20))

        # 绘制表格
        surface.blit(title_surf, title_rect)
        surface.blit(value_surf, value_rect)

    # 显示控制条
    def display_bar(self, surface, value, max_value, selected):

        # 控制条位置
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        # 神奇的语法
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        # 控制条选项
        full_height = bottom[1] - top[1]
        # 获得选项当前的相对高度
        relative_number = (value / max_value) * full_height
        # 浮标所在的位置
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_number, 30, 10)

        # 绘制选项
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    # 触发控制
    def trigger(self, move):
        self.move = move
        selected_attribute = list(volumes.keys())[self.index]

        # 控制音量
        if max_volume[selected_attribute] >= volumes[selected_attribute] >= min_volume:
            volumes[selected_attribute] += self.move

        if volumes[selected_attribute] > max_volume[selected_attribute]:
            volumes[selected_attribute] = max_volume[selected_attribute]

        if volumes[selected_attribute] < min_volume:
            volumes[selected_attribute] = min_volume

    def display(self, surface, selection_num, name, value, max_value):
        # 绘制选中框
        if self.index == selection_num:
            # 选中框的颜色与其他的不同
            pygame.draw.rect(surface, BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, self.index == selection_num)
        self.display_bar(surface, value, max_value, self.index == selection_num)
