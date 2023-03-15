# 作   者：许晨昊
# 开发日期：9/3/2023
import pygame
from settings import *
from player import Player


# 负责绘制背景和精灵的类
class Level:
    def __init__(self):
        self.player1 = None
        self.player = None
        # 获取当前显示的Surface对象（这里应该是整个显示窗口？）（官网文档没有看懂，存疑）
        self.display_surface = pygame.display.get_surface()
        # 创建sprite的容器all_sprites(全局变量？)
        self.all_sprites = pygame.sprite.Group()
        self.setup()

    def setup(self):
        # 创建并设置精灵(all_sprite实体) (player调用的是sprite父类初始化方法）
        # player重写了sprites父类的方法，实例化以后会在group里添加一个精灵
        self.player = Player((640, 360), self.all_sprites)

    def run(self, dt):
        # 填充背景（显示区域）
        self.display_surface.fill('black')
        # 绘制精灵组（all_sprite)到显示区域（surface)
        self.all_sprites.draw(self.display_surface)
        # 刷新精灵组(文档找不到详细说明，个人理解：直接按顺序调用group中每个实例化的sprite中的update()）
        self.all_sprites.update(dt)
