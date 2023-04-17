# 作   者：许晨昊
# 开发日期：2023/4/07

import pygame
from timer import Timer
from settings import *


class Start:

    def __init__(self):
        # 基本设置
        self.options = ['start', 'setting', 'exit']
        self.main_rect = None
        self.menu_top = None
        self.total_height = None
        self.text_surfs = None
        self.start = True

        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)

        # 菜单窗口属性
        self.width = 400
        self.space = 10
        self.padding = 8

        # 菜单内部
        # 获得所有物品
        self.setup()

        # 移动选择
        self.index = 0
        self.timer = Timer(200)

    def setup(self):
        # 创建物品文本显示属性
        self.text_surfs = []
        self.total_height = 0

        # 遍历选项添加图片
        for item in self.options:
            # 第二个参数是抗锯齿
            # font.render用于把字体生成图片
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        # 确定显示框的位置
        # 计算总高
        self.total_height += (len(self.text_surfs) - 1) + self.space
        # 菜单顶部位置
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        # 生成菜单矩形
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

    def input(self):
        keys = pygame.key.get_pressed()

        # 时间到了就关闭计时器
        self.timer.update()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()

            if keys[pygame.K_RETURN]:
                self.timer.activate()

                # 获得物品
                current_item = self.options[self.index]
                print(current_item)
                if self.index == 0:
                    self.start = False

        # 控制index的范围
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0

    def show_entry(self, text_surf, top, selected):
        # 文本背景条
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        # 文本
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        if selected:
            # draw.rect方法如果width参数>0 （这里是4） 就不会填充，而是变为设置描线宽度
            pygame.draw.rect(self.display_surface, 'pink', bg_rect, 4, 4)

    def update(self):
        self.input()

        for text_index, text_surf in enumerate(self.text_surfs):
            # 确定每个文字框的顶部位置
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            # 获得所有物品数量
            self.show_entry(text_surf, top, self.index == text_index)
