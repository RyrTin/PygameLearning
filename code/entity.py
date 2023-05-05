# 作   者：许晨昊
# 开发日期：2023/4/19


import pygame
from math import sin


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.value = None
        self.frame_index = 0
        self.animation_speed = 0.06  # (把dt固定下来了)
        self.direction = pygame.math.Vector2()

    def move(self, speed):
        # 标准化速度
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # 根据方向移动碰撞盒
        self.hitbox.x += self.direction.x * speed
        # 判断一次碰撞
        self.collision('horizontal')
        # 垂直方向同理
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        # 将逻辑位置与碰撞盒位置同步
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        # 碰撞后修正位置（同理）
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                # 判断是否碰撞（返回True or False）
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def wave_value(self):
        self.value = sin(pygame.time.get_ticks())
        # 利用三角函数周期性的返回255和0 （学到了）
        if self.value >= 0:
            return 255
        else:
            return 0
