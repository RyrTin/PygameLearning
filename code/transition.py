# 作   者：许晨昊
# 开发日期：17/3/2023

import pygame
from data import *


class Transition:
    def __init__(self):
        # 设置
        # 获取整个窗口作为显示区
        self.display_surface = pygame.display.get_surface()

        # 叠加图片
        # 生成一坨和屏幕一样大的图片
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -3
        self.fade_in = True
        self.fade_out = False

    def fadein(self):
        # 禁止移动

        # 颜色随着时间变化
        self.color += self.speed
        # 防止颜色超出(0,255)
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.fade_out = True
        # 生成一个渐变黑的图片(调用一次变黑一点)
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    def fadeout(self):
        self.color += self.speed

        if self.color > 255:
            self.color = 255
            self.speed *= -1
            self.fade_out = False
        # 生成一个渐变白的图片(调用一次变黑一点)
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

