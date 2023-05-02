import pygame
from data import *


# 用于创建贴图（瓦片）
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILE_SIZE, TILE_SIZE))):

        super().__init__(groups)
        # 区分可视/非可视
        self.sprite_type = sprite_type
        # y轴偏移（微调碰撞区）
        y_offset = HITBOX_OFFSET[sprite_type]
        # 贴图
        self.image = surface

        # 如果是物品（树木等） 修改一点位置
        if sprite_type == 'object':
            self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - TILE_SIZE - 10))
        else:
            self.rect = self.image.get_rect(topleft=pos)
        # 生成碰撞箱
        self.hitbox = self.rect.inflate(0, y_offset)
