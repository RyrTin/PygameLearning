# 作   者：许晨昊
# 开发日期：17/3/2023

import pygame
from settings import *


class Transition:
    def __init__(self, reset, player):
        # 设置
        # 获取整个窗口作为显示区
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # 叠加图片
        # 生成一坨和屏幕一样大的图片
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):

        # 颜色随着时间变化
        self.color += self.speed
        # 防止颜色超出(0,255)
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            # 重置属性
            self.reset()
            self.player.timers['time'].activate()
        if self.color > 255:
            self.color = 255
            self.speed *= -1
            self.player.sleep = False

        # 生成一个渐变黑的图片(调用一次变黑一点)
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
