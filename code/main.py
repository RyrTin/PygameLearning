import sys
import pygame
from settings import *
from level import Level


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
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # clock.tick()将统计当前tick和上一此tick的时间间隔，单位为s，通常/1000 以转化为毫秒
            # 上一帧结束了，这帧准备开始，也就是两次动作之间的间隔时间，通过这个时间来控制精灵图片的位移
            # 这样便保证了在不同帧数下，一秒内各种精灵贴图的位移是固定的、
            # 这里传给后面一个dt 所有需要移动的方法都以这个dt为参数
            dt = self.clock.tick() / 1000
            # print(dt)
            # 调用level中的run方法
            self.level.run(dt)
            # 刷新画面(只要改变就刷新，所以不用固定刷新速度）
            pygame.display.update()


if __name__ == '__main__':
    # print('start')
    game = Game()
    game.run()
