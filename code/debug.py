# 作   者：许晨昊
# 开发日期：2023/5/2

import pygame,sys

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
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()

        self.confirm = Confirm()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # self.screen.fill(WATER_COLOR)

            self.confirm.display()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
