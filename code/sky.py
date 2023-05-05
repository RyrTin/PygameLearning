# 作   者：许晨昊
# 开发日期：2023/3/23
import pygame
from data import *
from support import import_folder
from sprite import Generic
from random import randint, choice


class Sky:
    def __init__(self):
        # 获取显示区域
        self.display_surface = pygame.display.get_surface()
        # 创建显示图像 Surface((width, height), flags=0, depth=0, masks=None) -> Surface 颜色默认全黑
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        # 用个元组确保不能变
        self.end_color = (38, 101, 189)

    def display(self, dt):
        # 迭代开始颜色的三原色，直到达到结束颜色
        for index, value in enumerate(self.end_color):
            if self.start_color[index] > value:
                self.start_color[index] = (self.start_color[index] - 0.6 * dt)

        self.full_surf.fill(self.start_color)
        self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


class Drop(Generic):
    # 这里参考particle精灵的方法
    def __init__(self, surf, pos, moving, groups, z):
        # 初始化
        super().__init__(pos, surf, groups, z)
        # 随机一个生命周期
        self.lifetime = randint(400, 500)
        # 获取当前时间
        self.start_time = pygame.time.get_ticks()

        # 判定移动
        self.moving = moving
        if self.moving:
            # 移动三属性：位置，方向，速度
            self.pos = pygame.math.Vector2(self.rect.topleft)
            # 斜着向左下方下雨，所以方向向量设置成(-2,4)
            self.direction = pygame.math.Vector2(-2, 4)
            # 随机一个速度
            self.speed = randint(200, 250)

    # 重写update
    def update(self, dt):
        # 实现移动
        if self.moving:
            self.pos += self.direction * self.speed * dt
            # 这里详细说一下rect的属性是四个顶点的位置
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # 计时器
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites):
        # 传入组
        self.all_sprites = all_sprites
        # 导入素材
        self.rain_drops = import_folder('../graphics/rain/drops')
        self.rain_floor = import_folder('../graphics/rain/floor')
        self.floor_w, self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size()

    def create_floor(self):
        # 每一个水花都是独立的精灵(每一帧都会创建一个，帧数越低雨水越少？)
        Drop(
            surf=choice(self.rain_floor),
            # 在全地图的范围内随机挑选生成位置
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=False,
            groups=self.all_sprites,
            z=LAYERS['rain floor'])

    def create_drops(self):
        # 每一滴雨水都是独立的精灵
        Drop(
            surf=choice(self.rain_drops),
            # 同上
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            # 雨水会移动所以改成true
            moving=True,
            groups=self.all_sprites,
            z=LAYERS['rain drops'])

    def update(self):
        self.create_floor()
        self.create_drops()
