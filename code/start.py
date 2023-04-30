# 作   者：许晨昊
# 开发日期：2023/4/07

import pygame
import sys
from timer import Timer
from data import *
from settings import *
from support import *


class Start:

    def __init__(self):
        # 基本设置
        self.title_surf = None
        self.options = ['start', 'sound setting', 'exit']
        self.bg_list = {}
        self.frame_index = 0
        self.rect = None
        self.image = None
        self.main_rect = None
        self.menu_top = None
        self.total_height = None
        self.text_surfs = None
        self.active = True
        # 设置初始化
        self.settings = Settings()
        self.settings_active = False

        self.display_surface = pygame.display.get_surface()
        # 设置文本字体
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        # 设置标题字体
        self.font_title = pygame.font.Font('../font/LycheeSoda.ttf', 120)

        # 菜单窗口属性
        self.width = 400
        self.space = 10
        self.padding = 8

        # 菜单内部
        # 获得所有物品
        self.setup()
        # 载入背景图片
        self.import_assets()
        # 移动选择
        self.index = 0
        self.timer = Timer(200)

        # 初始化背景音乐
        self.music = pygame.mixer.Sound('../audio/start.mp3')
        self.music.set_volume(volumes['bgm'])
        self.music.play(loops=-1)

    def import_assets(self):

        # 动作组名称词典
        # 调用一个import_folder方法来导入每个动作组的所有图片
        full_path = '../graphics/start'

        self.bg_list = import_folder_start(full_path)
        # print(self.bg_list)

    def animate(self, dt):
        self.frame_index += 3 * dt
        # 这里取余数比直接归零慢
        if self.frame_index >= 82:
            self.frame_index = 0

        self.image = self.bg_list[int(self.frame_index)]
        self.rect = self.image.get_rect()
        self.display_surface.blit(self.image, self.rect)

    def setup(self):
        # 创建物品文本显示属性
        self.text_surfs = []
        self.total_height = 0
        self.title_surf = self.font_title.render('Pyland', False, 'Black')

        # 遍历选项添加图片
        for item in self.options:
            # 第二个参数是抗锯齿
            # font.render用于把字体生成图片
            text_surf = self.font.render(item, False, 'Black')
            # 把surface和位置信息存到list中，最后用show_entry绘制出来
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        # 确定显示框的位置
        # 计算总高
        self.total_height += (len(self.text_surfs) - 1) + self.space
        # 菜单顶部位置
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2 + 100
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

                # 获得选项
                current_item = self.options[self.index]
                # print(current_item)
                if self.index == 0:
                    self.active = False
                if self.index == 1:
                    self.toggle_settings()
                if self.index == 2:
                    pygame.quit()
                    sys.exit()

        # 控制index的范围
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0

    def show_option(self, text_surf, top, selected):
        # 创建文本背景条矩形
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        # 创建文本矩形
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        if selected:
            # draw.rect方法如果width参数>0 （这里是4） 就不会填充，而是变为设置描线宽度
            pygame.draw.rect(self.display_surface, 'pink', bg_rect, 4, 4)

    def show_title(self, text_surf):
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT/2 - 120))
        self.display_surface.blit(text_surf, text_rect)

    def set_volume(self, value):
        self.music.set_volume(value)

    def toggle_settings(self, ):
        # 切换
        self.settings_active = not self.settings_active

    def update(self, dt):
        self.display_surface.fill('black')
        self.animate(dt)

        if self.settings_active:
            self.settings.display()

        else:

            self.input()

            self.show_title(self.title_surf)
            for text_index, text_surf in enumerate(self.text_surfs):
                # 确定每个文字框的顶部位置
                top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
                # 获得所有物品数量
                self.show_option(text_surf, top, self.index == text_index)
