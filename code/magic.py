import pygame
from settings import *
from random import randint


class MagicPlayer:
    def __init__(self, animation_player):
        # 动画播放器
        self.animation_player = animation_player

        # 魔法音效
        self.sounds = {
            'heal': pygame.mixer.Sound('../audio/heal.wav'),
            'flame': pygame.mixer.Sound('../audio/Fire.wav')
        }

    # 治疗魔法
    def heal(self, player, strength, cost, groups):

        # 能量值充足则治疗
        if player.energy >= cost:
            # 音效
            self.sounds['heal'].play()
            player.health += strength
            player.energy -= cost
            # 治疗量无法溢出
            if player.health >= player.stats['health']:
                player.health = player.stats['health']
            # 播放治疗粒子
            self.animation_player.create_particles('aura', player.rect.center, groups)
            self.animation_player.create_particles('heal', player.rect.center, groups)

    # 火焰魔法
    def flame(self, player, cost, groups):

        # 能量充足则释放成功
        if player.energy >= cost:
            player.energy -= cost
            self.sounds['flame'].play()

            # 根据角色状态判断释放方向
            if player.status.split('_')[0] == 'right':
                direction = pygame.math.Vector2(1, 0)
            elif player.status.split('_')[0] == 'left':
                direction = pygame.math.Vector2(-1, 0)
            elif player.status.split('_')[0] == 'up':
                direction = pygame.math.Vector2(0, -1)
            else:
                direction = pygame.math.Vector2(0, 1)

            # 多次播放动画帧
            # 相当于创建了五颗粒子（每一颗独立有动画帧）
            for i in range(1, 6):
                if direction.x:  # 水平
                    # 控制火焰逐渐远离玩家
                    offset_x = (direction.x * i) * TILE_SIZE
                    x = player.rect.centerx + offset_x + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    y = player.rect.centery + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    # 创建动画帧
                    self.animation_player.create_particles('flame', (x, y), groups)
                else:  # 垂直
                    # 同理
                    offset_y = (direction.y * i) * TILE_SIZE
                    x = player.rect.centerx + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILE_SIZE // 3, TILE_SIZE // 3)
                    # 创建动画帧
                    self.animation_player.create_particles('flame', (x, y), groups)
