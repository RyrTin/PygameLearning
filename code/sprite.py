# 作   者：许晨昊
# 开发日期：15/3/2023

import pygame
from settings import *


# 因为有虚拟的z轴（用于区分图层）所以创建Sprite的子类
class Generic(pygame.sprite.Sprite):
    # 类似于Player ，但是需要很多的image作为surf（其实是差不多的东西）
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z


# 水有动态帧，所以创建Generic的子类
class Water(Generic):
    def __init__(self, pos, frames, groups):
        # 动画设置
        self.frames = frames
        self.frame_index = 0

        # 精灵初始化
        super().__init__(
            pos=pos,
            surf=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5 * dt
        # 这里取余数比直接归零慢
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


# 花朵同理
class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)


class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)
