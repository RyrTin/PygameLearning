# 作   者：许晨昊
# 开发日期：2023/4/2

import pygame, sys

from start import Start
from home import Home
from level import Level
from confirm import *
from settings import *


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Pyland')
        self.clock = pygame.time.Clock()
        # self.home = Home()
        self.level = Level()
        # self.confirm = Confirm()

    def run(self):
        while self.level.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and not self.level.enter and not self.level.win:
                        self.level.kill_all()

            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
