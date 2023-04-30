# 作   者：许晨昊
# 开发日期：9/3/2023

# from import * 可以直接使用函数 不必指定模块 比直接import 方便
import sys
import pygame
from data import *
from home import Home
from start import Start


# 主程序
class Game:
    def __init__(self):
        # 初始化pygame模块

        pygame.init()
        # 设置窗口大小
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 设置窗口标题
        pygame.display.set_caption('Pyland')
        # 初始化一个时钟对象
        self.clock = pygame.time.Clock()
        # 实例化 Level类 ，用于生成背景和精灵
        self.start = Start()
        self.home = None

    def run(self):
        while self.start.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.start.toggle_settings()

            # print(dt)
            # 调用level中的run方法
            dt = self.clock.tick() / 1000
            self.start.update(dt)
            self.start.set_volume(volumes['bgm'])
            pygame.display.update()

        # 放在前面实例化会导致bgm提前出来
        self.home = Home()
        # 音乐淡出，进入游戏
        self.start.music.fadeout(300)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # clock.tick()将统计当前tick和上一此调用tick的时间间隔，单位为s，通常/1000 以转化为毫秒
            # 获得一个相对稳定的dt（其实是上一帧的运行时间），通过这个时间来控制精灵图片的位移
            # 这样便保证了在不同帧数下，相同时间内各种精灵贴图的位移是固定的
            # 这里传给后面一个dt 所有需要移动的方法都以这个dt为参数 但是只控制距离，不控制时间，具体一帧多久看电脑(设置)
            # 也就是说一直是以上一帧跑了多久来控制下一帧的速度(运行距离),而且第一帧是不动的（延迟控制方式）
            # tick中可以固定帧数
            dt = self.clock.tick() / 1000
            # print(dt)
            # 调用level中的run方法
            self.home.run(dt)
            # 刷新画面(只要改变就刷新，所以不用固定刷新速度）
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
