# 作   者：许晨昊
# 开发日期：2023/4/20

import pygame
from data import *
from support import *
from entity import *
from confirm import *
import random


class LevelPlayer(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):

        # 初始化
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/character/down/0.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(HITBOX_OFFSET['player'])

        # 图像设置
        self.import_player_assets()
        self.status = 'down'

        # 行动
        self.attacking = False
        self.attack_cooldown = 100
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites

        # 武器设置
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon_list = list(random.sample(weapon_data.keys(), 2))

        # print(self.weapon_list)
        self.weapon = self.weapon_list[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        # 魔法设置
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # 玩家状态
        self.stats = player_stats
        self.max_stats = player_max_stats

        # 血量（测试进入半血）
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.attack = self.stats['attack']
        self.m_atk = self.stats['magic']
        self.money = 0
        self.speed = self.stats['speed']

        # 界面状态
        self.quit = False
        self.game_paused = False
        self.win = False

        # 攻击计时器
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # 导入声音
        self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
        self.weapon_attack_sound.set_volume(volumes['action'])

    def import_player_assets(self):

        character_path = '../graphics/character/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        if not self.attacking:

            keys = pygame.key.get_pressed()

            # 玩家移动
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # 使用攻击
            if keys[pygame.K_j]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()

            # 使用技能
            if keys[pygame.K_k]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)

            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.weapon_index < len(self.weapon_list) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0

                self.weapon = self.weapon_list[self.weapon_index]

            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()

                if self.magic_index < len(list(magic_data.keys())) - 1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0

                self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):

        # 待机状态
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status = self.status + '_idle'

        # 攻击状态
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if 'attack' not in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    # 攻击冷却
    def cooldowns(self):

        # 获得攻击发动时间
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False

            # 攻击模型需要早于冷却消失 否则无限击退
            if current_time - self.attack_time >= self.attack_cooldown:
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self):

        animation = self.animations[self.status]

        # 循环播放动画帧
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # 设置图像
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # 闪烁（受伤）
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.attack
        weapon_damage = weapon_data[self.weapon]['damage']
        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.m_atk
        spell_damage = magic_data[self.magic]['strength']
        return base_damage + spell_damage

    def update(self):

        self.weapon_attack_sound.set_volume(volumes['action'])
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats['speed'])
