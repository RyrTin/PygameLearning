import pygame


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        # 根据玩家状态判断方向
        direction = player.status.split('_')[0]

        # 读取武器图片
        full_path = f'../graphics/weapons/{player.weapon}/{direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # 根据方向选择武器图片
        if direction == 'right':
            self.rect = self.image.get_rect(midleft=player.hitbox.midright + pygame.math.Vector2(10, 20))
        elif direction == 'left':
            self.rect = self.image.get_rect(midright=player.hitbox.midleft + pygame.math.Vector2(-10, 20))
        elif direction == 'down':
            self.rect = self.image.get_rect(midtop=player.hitbox.midbottom + pygame.math.Vector2(-10, 12))
        else:
            self.rect = self.image.get_rect(midbottom=player.hitbox.midtop + pygame.math.Vector2(-10, 0))
