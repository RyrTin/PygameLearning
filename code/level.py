# 作   者：许晨昊
# 开发日期：9/3/2023
import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprite import *
from pytmx.util_pygame import load_pygame
from support import *


# 负责绘制精灵的类
class Level:
    def __init__(self):
        self.player1 = None
        self.player = None
        # 获取当前显示的Surface对象（这里应该是整个显示窗口？）（官网文档没有看懂，存疑）
        self.display_surface = pygame.display.get_surface()
        # 创建sprite的容器all_sprites(这里使用对Group重写的CameraGroup)
        self.all_sprites = CameraGroup()
        # 实例化一个player,player是整个程序的核心部分
        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        # 把各种图层信息保存在方格里的地图
        tmx_data = load_pygame('../data/map.tmx')

        # 房子
        # 从每个图层中获取相应的物品贴图和位置信息，并用通用精灵方式生成精灵
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # 栅栏
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # 水
        water_frames = import_folder('../graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        # 树
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, self.all_sprites, obj.name)
        # 野花
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, self.all_sprites)

        # 创建并设置精灵(all_sprite实体) (player调用的是sprite父类初始化方法）
        # player重写了sprites父类的方法，实例化以后会在group里添加一个精灵
        self.player = Player((640, 360), self.all_sprites)

        # 创建通用精灵（有图片和位置的东西都可以视为精灵） tips:创建的先后顺序决定谁在上面的图层,所以要添加z轴。
        Generic(
            pos=(0, 0),
            surf=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground']
        )

    def run(self, dt):
        # 填充背景（显示区域）
        # self.display_surface.fill('black')
        # 绘制精灵组（all_sprite)到显示区域（surface)
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.custom_draw(self.player)
        # 刷新精灵组(文档找不到详细说明，个人理解：直接按顺序调用group中每个实例化的sprite中的update()）
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # 获取当前显示区域
        self.display_surface = pygame.display.get_surface()
        # 相机位移量
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # 为什么需要player 因为player是参照物，其他精灵需要根据player改变自己位置
        # 用两个参数确定Player和Camera中心的关系,即位移量
        # x轴方向的位移量
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        # y轴方向的位移量
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            # 按顺序从底层图层开始画，遍历每一个优先级，然后遍历在这个优先级的所有精灵，找到自己的位置后刷新精灵
            # 如果一个图层的位置更靠下 根据透视关系她应该遮挡上方的图层，排序是实现透视关系的一个好的解决办法
            # lambda 匿名函数用法：  lambda (参数） ： 方法
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    # 位移矩阵初始化 复制当前需要位移的精灵的位置
                    offset_rect = sprite.rect.copy()
                    # 相对位移是相反的所以减去位移
                    offset_rect.center -= self.offset
                    # 刷新所有精灵位移后的图像
                    self.display_surface.blit(sprite.image, offset_rect)
