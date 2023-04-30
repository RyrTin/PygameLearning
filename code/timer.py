# 作   者：许晨昊
# 开发日期：15/3/2023

import pygame


class Timer:
    def __init__(self, duration, func=None):

        self.duration = duration
        self.func = func
        self.start_time = 0
        self.stop_time = 0
        self.active = False

    def pass_time(self):
        # start_time在deactivate后依然有效，只在下次启动时刷新
        return 2*(pygame.time.get_ticks() - self.start_time) + self.stop_time

    def activate(self):
        # 激活计时器
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def reactivate(self):
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        # 关闭计时器
        self.active = False

    def stop(self):
        # 获得暂停时的时间
        self.stop_time = self.pass_time()

    def update(self):
        # 获取当前时间
        current_time = pygame.time.get_ticks()
        # 检测是否超时
        if current_time - self.start_time >= self.duration - self.stop_time:
            if self.func and self.active:
                self.func()
            # 执行方法后立刻关闭计时器
            self.deactivate()

