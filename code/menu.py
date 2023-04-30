# 作   者：许晨昊
# 开发日期：24/3/2023

import pygame
from data import *
from timer import Timer


class Menu:
    def __init__(self, player, toggle_menu):
        # 基本设置
        self.sell_text = None
        self.buy_text = None
        self.main_rect = None
        self.menu_top = None
        self.total_height = None
        self.text_surfs = None
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)

        # 菜单窗口属性
        self.width = 400
        self.space = 10
        self.padding = 8

        # 菜单内部
        # 获得所有物品
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()

        # 移动选择
        self.index = 0
        self.timer = Timer(200)

    def display_money(self):
        # 获得文字图片
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        # 添加背景（个人觉得不好看，后面可以注释掉）
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 6)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):

        # 创建物品文本显示属性
        self.text_surfs = []
        self.total_height = 0

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

        # 购买/出售 文本
        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')

    def input(self):
        keys = pygame.key.get_pressed()
        # 时间到了就关闭计时器
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            # 把菜单active置反，关闭菜单
            self.toggle_menu()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()

            if keys[pygame.K_SPACE]:
                self.timer.activate()

                # 获得物品
                current_item = self.options[self.index]
                # print(current_item)

                # 出售
                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                # 购买
                else:
                    seed_price = PURCHASE_PRICES[current_item]
                    if self.player.money >= seed_price:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= PURCHASE_PRICES[current_item]

        # 控制index的范围
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0

    def show_entry(self, text_surf, amount, top, selected):
        # 文本背景条
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        # 文本
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        # 数量
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        # 选择
        if selected:
            # draw.rect方法如果width参数>0 （这里是4） 就不会填充，而是变为设置描线宽度
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)

            # 不同区域显示不同字符
            if self.index <= self.sell_border:
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 250, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 250, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)

    def update(self):
        self.input()
        self.display_money()

        for text_index, text_surf in enumerate(self.text_surfs):
            # 确定每个文字框的顶部位置
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            # 获得所有物品数量
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)

            # self.display_surface.blit(text_surf, (300, text_index * 50))
