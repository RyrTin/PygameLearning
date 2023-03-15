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
            # delta time 可以保证物体每秒的移动距离相等
            dt = self.clock.tick() / 1000
            # 调用level中的run方法
            self.level.run(dt)
            # 刷新画面(只要改变就刷新，所以不用固定刷新速度）
            pygame.display.update()


if __name__ == '__main__':
    # print('start')
    game = Game()
    game.run()
