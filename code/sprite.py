# 作   者：许晨昊
# 开发日期：2023/3/15
import pygame
from data import *
from random import randint, choice
from timer import Timer


# 因为有虚拟的z轴（用于区分图层）所以创建Sprite的子类
class Generic(pygame.sprite.Sprite):
    # 类似于Player ，但是需要很多的image作为surf（其实是差不多的东西）
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


# 水有动态帧，所以创建Generic的子类
class Water(Generic):
    def __init__(self, pos, frames, groups):
        # 动画设置
        self.frames = frames
        self.frame_index = 0

        # 精灵初始化
        super().__init__(
            pos=pos,
            surf=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5 * dt
        # 这里取余数比直接归零慢
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class Interaction(Generic):
    def __init__(self, pos, size, groups, name, player):

        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name
        self.player = player
        # 获得与玩家的距离
        self.action_radius = 100
        self.status = None
        self.font = pygame.font.Font(UI_FONT, 30)
        self.display_surface = pygame.display.get_surface()

    def get_player_distance_direction(self):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(self.player.rect.center)
        # 获得欧氏距离
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            # 标准化距离（把距离转化为方向）
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

        # 获得状态

    def get_status(self):
        # 获得距离
        distance = self.get_player_distance_direction()[0]
        if distance <= self.action_radius:
            self.status = 'active'
        # 待机
        else:
            self.status = 'idle'

        # print(self.status)
        # 获得行为（根据状态）

    def display_tip(self):
        if self.name == 'Bed':
            word = 'Sleep'
        elif self.name == 'Trader':
            word = 'Shop'
        elif self.name == 'Fight':
            word = 'Level'
        title_surf = self.font.render('Press Enter To ' + word, False, 'Black')
        title_rect = title_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 4 / 5))
        self.display_surface.blit(title_surf, title_rect)

    def actions(self):
        if self.status == 'active':
            self.display_tip()

    def update(self):
        self.get_status()
        self.actions()


# 花朵同理
class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


# 树有多种状态所以需要很多不同的方法
# 因此当一个精灵需要被改变时通常在他的内部加一些方法
class Tree(Generic):
    def __init__(self, pos, surf, groups, name, player_add):
        super().__init__(pos, surf, groups)
        # 属性
        self.health = 5
        self.alive = True
        stump_path = f'../graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()

        # 获取苹果贴图
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png')
        # 获取苹果位置表
        self.apple_pos = APPLE_POS[name]
        # 创建苹果精灵组
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

        # 声音
        self.axe_sound = pygame.mixer.Sound('../audio/axe.mp3')

    def damage(self):

        # 砍树
        self.health -= 1

        # 播放声音
        self.axe_sound.set_volume(volumes['item'])
        self.axe_sound.play()

        # 移除苹果
        # group.sprites()返回一个精灵列表
        if len(self.apple_sprites.sprites()) > 0:
            # random.choice从非空表中随机选择一个数据
            random_apple = choice(self.apple_sprites.sprites())
            # print('remove')
            # 调用粒子精灵
            Particle(
                pos=random_apple.rect.topleft,
                surf=random_apple.image,
                groups=self.groups()[0],
                z=LAYERS['fruit'])
            # 玩家获得一个苹果
            self.player_add('apple')
            # kill方法可以消除精灵
            random_apple.kill()

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                # 创建苹果精灵(可视化），放到精灵组和苹果组里
                Generic(
                    pos=(x, y),
                    surf=self.apple_surf,
                    groups=[self.apple_sprites, self.groups()[0]],
                    z=LAYERS['fruit']
                )

    def check_death(self):
        if self.health <= 0:
            # 调用粒子精灵
            Particle(
                pos=self.rect.topleft,
                surf=self.image,
                groups=self.groups()[0],
                z=LAYERS['fruit'],
                duration=500
            )
            # 替换树木贴图为树桩
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            # 玩家获得一个木头
            self.player_add('wood')

    def update(self, dt):
        if self.alive:
            self.check_death()


# 粒子
class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        # 粒子存在时间短所以内置计时器
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        # 白色图层
        # 蒙版这里的官方文档看不懂
        # 创建给定图片的蒙版(设置不透明区域为1，透明区域为0)
        mask_surf = pygame.mask.from_surface(self.image)
        # 把蒙版转回一个表面(实际效果就是原来的图片有像素的区域变白，没有像素的区域变黑)
        new_surf = mask_surf.to_surface()
        # 设置当前表面的颜色键，和颜色键相同的颜色会变得透明（这里设置成黑，实际效果是让之前黑的地方变透明）
        new_surf.set_colorkey((0, 0, 0))
        # 最终把这个白苹果效果呈现出来
        self.image = new_surf

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()
