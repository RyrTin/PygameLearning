import pygame
from settings import *
from entity import *
from support import *


class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_money):

        # 初始化设置
        super().__init__(groups)
        self.animations = None
        # 设置精灵类型
        self.sprite_type = 'enemy'

        # 贴图设置
        # 载入怪物贴图
        self.import_graphics(monster_name)
        # 设置初始状态为待机
        self.status = 'idle'
        # 根据状态选择贴图
        self.image = self.animations[self.status][self.frame_index]

        # 移动
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # 怪物状态、信息
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.money = monster_info['money']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # 玩家交互设置（攻击玩家）
        # 攻击判定
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_money = add_money

        # 无敌帧设置
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # 怪物声音
        self.death_sound = pygame.mixer.Sound('../audio/death.wav')
        self.hit_sound = pygame.mixer.Sound('../audio/hit.wav')
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.death_sound.set_volume(volumes['action'])
        self.hit_sound.set_volume(volumes['action'])
        self.attack_sound.set_volume(volumes['action'])

    # 加载图片
    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'../graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    # 获得与玩家的距离
    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        # 获得欧氏距离
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            # 标准化距离（把距离转化为方向）
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

    # 获得状态
    def get_status(self, player):

        # 获得距离
        distance = self.get_player_distance_direction(player)[0]

        # 距离小于攻击半径且可以攻击
        if distance <= self.attack_radius and self.can_attack:
            # 如果当前不是攻击帧 ，重置动画帧 ，状态设置为攻击
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'

        # 距离小于警觉半径则移动向玩家
        elif distance <= self.notice_radius:
            self.status = 'move'

        # 待机
        else:
            self.status = 'idle'

    # 获得行为（根据状态）
    def actions(self, player):
        if self.status == 'attack':
            # 开始攻击
            self.attack_time = pygame.time.get_ticks()
            # 攻击玩家（造成伤害）
            self.damage_player(self.attack_damage, self.attack_type)
            # 播放音效
            self.attack_sound.play()
        elif self.status == 'move':
            # 朝玩家跑
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            # 移速清空（待机）
            self.direction = pygame.math.Vector2()

    # 播放动画
    def animate(self):
        # 根据状态获得动画（列表）
        animation = self.animations[self.status]

        # 更新动画帧
        self.frame_index += self.animation_speed

        # 动画帧结束
        if self.frame_index >= len(animation):
            # 如果在攻击  结束攻击
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        # 获得当前帧贴图
        self.image = animation[int(self.frame_index)]
        # 获得贴图矩形
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # 受伤时闪烁
        if not self.vulnerable:
            # 反复输出0 和 255
            alpha = self.wave_value()
            # 反复修改透明度 营造闪烁的感觉
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    # 冷却时间（攻击和受击）
    def cooldowns(self):
        # 获得当前时间
        current_time = pygame.time.get_ticks()
        # 攻击计时 时间到了切换为可攻击状态
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        # 受击计时，到时间了切换为可攻击（非无敌帧）
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    # 受到攻击
    def get_damage(self, player, attack_type):

        # 可以被攻击时
        if self.vulnerable:
            # 播放声音
            self.hit_sound.play()

            # 获得方向
            self.direction = self.get_player_distance_direction(player)[1]

            # 受击时是武器
            if attack_type == 'weapon':
                # 扣血
                self.health -= player.get_full_weapon_damage()
            # 魔法
            else:
                # 扣血
                self.health -= player.get_full_magic_damage()

            # 记录受击时间
            self.hit_time = pygame.time.get_ticks()
            # 标志进入无敌帧
            self.vulnerable = False

    def check_death(self):

        # 看看噶了没
        if self.health <= 0:
            # 啊我死了
            self.kill()
            # 触发死亡粒子特效
            self.trigger_death_particles(self.rect.center, self.monster_name)
            # 播放击杀音效
            self.death_sound.play()
            self.add_money(self.money)

    # 受击效果
    def hit_reaction(self):

        # 是否在无敌阵
        if not self.vulnerable:
            # 往反方向退
            self.direction *= -self.resistance

    def update(self):

        self.death_sound.set_volume(volumes['action'])
        self.hit_sound.set_volume(volumes['action'])
        self.attack_sound.set_volume(volumes['action'])
        # 每次call sprite的update方法时自动更新
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self, player):

        # 需要自己调用 与玩家交互时的更新方法
        self.get_status(player)
        self.actions(player)
