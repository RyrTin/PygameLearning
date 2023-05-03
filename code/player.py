# 作   者：许晨昊
# 开发日期：14/3/2023
import math

import pygame

from data import *
from support import *
from timer import Timer


# 负责初始化精灵的类
# 主要被level导包
# 重写sprite类
class Player(pygame.sprite.Sprite):
    # tips:大部分与玩家相关的功能都应该与Player有关，所以实现一个方法后必须考虑放在Player的什么位置
    # 比如这里需要跟树木精灵 tree_sprites 进行交互，所以也应该作为参数传到Player的类中
    # 初始化。
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop, toggle_fight):
        # 调用父类方法初始化
        super().__init__(group)
        # 主要有各种功能素材，属性的初始化
        # 导入动画素材包
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': [],
                           }
        self.import_assets()

        # 角色初始状态为面朝下
        self.status = 'down_idle'
        self.frame_index = 0

        # 初始化精灵
        # 设置精灵图像
        self.image = self.animations[self.status][self.frame_index]
        # 设置精灵矩形（rect是一个矩形，大致包含整个图像的大小和位置信息）
        self.rect = self.image.get_rect(center=pos)
        # 设置精灵图层
        self.z = LAYERS['main']

        # 生命属性
        self.health = 5
        self.magic = 3

        # 移动属性：方向，位置，速度
        # 方向属性：使用一个2维向量保存移动方向
        self.direction = pygame.math.Vector2()
        # 位置属性
        self.pre_x = None
        self.pre_y = None
        self.pos = pygame.math.Vector2(self.rect.center)
        # 速度属性
        self.speed = 300

        # 碰撞检测！（狂喜） 拷贝一个精灵rect，适当缩小边缘，并且需要跟随精灵，这一点将在move方法里体现
        # 精细化碰撞盒，修改人物大小
        self.hitbox = self.rect.copy().inflate((-126, -80))
        self.collision_sprites = collision_sprites

        # 计时器(这里用词典形式保存实例化的计时器）
        # 计时器是重要的时间控制工具，主要控制某个方法的持续时间或按键响应次数等
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200),
            'switch': Timer(300),
            'time': Timer(420000)
        }
        # 初始化目标点
        self.target_pos = None

        # 工具
        # 建立字典和索引
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # 种子
        # 建立字典和索引
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # 树
        self.tree_sprites = tree_sprites

        # 交互
        self.interaction = interaction
        self.sleep = False
        self.fight = False

        # 玩家资产(词典)
        self.item_inventory = {
            'wood': 20,
            'apple': 20,
            'corn': 20,
            'tomato': 20
        }
        self.seed_inventory = {
            'corn': 5,
            'tomato': 5
        }
        self.money = 200

        # 土壤
        self.soil_layer = soil_layer

        # 商店
        self.toggle_shop = toggle_shop

        # 战斗
        self.toggle_fight = toggle_fight

        # 声音
        self.watering = pygame.mixer.Sound('../audio/water.mp3')
        # 音量
        self.watering.set_volume(volumes['action'])

        # 状态
        self.quit = False
        self.game_paused = False

    # 通过碰撞检测响应动作
    def use_tool(self):
        # print('tool use')
        # 使用锄头
        if self.selected_tool == 'hoe':
            # 土壤层受击判定
            self.soil_layer.get_hit(self.target_pos)

        # 使用斧头
        if self.selected_tool == 'axe':
            # 树木受击判定
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        # 使用水壶
        if self.selected_tool == 'water':
            # 浇水区受击判定
            self.soil_layer.water(self.target_pos)
            self.watering.play()

    # 获得目标点
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    # 使用工具
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            if self.soil_layer.plant_seed(self.target_pos, self.selected_seed):
                self.seed_inventory[self.selected_seed] -= 1

    # 导入素材
    def import_assets(self):

        # 动作组名称词典
        # 调用一个import_folder方法来导入每个动作组的所有图片
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation

            self.animations[animation] = import_folder(full_path)
        # print(self.animations)

    # 根据Sprite状态对照动画字典找到对应的动画帧
    def animate(self, dt):
        self.frame_index += 4 * dt
        # 这里取余数比直接归零慢
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        # 获取动画帧
        # 注意这个字典保存的是surface格式的文件
        self.image = self.animations[self.status][int(self.frame_index)]

    # 响应按键（大部分功能都必须由按键响应，是各类功能开始的部分）
    def input(self):
        keys = pygame.key.get_pressed()

        # 使用工具，睡觉，进入战斗时无法移动
        if not self.timers['tool use'].active and not self.sleep and not self.fight:
            # 控制方向
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # 控制工具
            # 事实上方法被运行一次以后计时器就被关闭了，所以这里可以不用约束
            if keys[pygame.K_j]:
                # 这里按下空格后activate持续了350ms
                # activate以后 get_status就能一直根据计时器的active状态使角色短时间内一直处于某种状态（控制动画时常）
                # 同时根据字典将方法传入Timer开始运作
                self.timers['tool use'].activate()
                # 使用工具时不能移动，所以初始化速度（即位移变为0，0）
                self.direction = pygame.math.Vector2()
                # 重置动画帧
                self.frame_index = 0
            # 切换工具(用计时器约束切换时间 以及切换条件，如不能在工具正在被使用时切换)
            if keys[pygame.K_q] and not self.timers['tool switch'].active and not self.timers['tool use'].active:
                # 计时器在激活期间按键落下的判定就不会触发 主要起到这个作用
                self.timers['tool switch'].activate()
                self.tool_index += 1
                # 我的想法：self.tool_index = self.tool_index % 3 效果一样但是取余会慢
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]
            # 控制种子
            if keys[pygame.K_k]:
                # 这里按下空格后activate持续了350ms
                self.timers['seed use'].activate()
                # 使用种子时不能移动，所以初始化速度（即位移变为0，0）
                self.direction = pygame.math.Vector2()
                # 重置动画帧
                self.frame_index = 0
                # print('use seed')
            # 切换种子
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                # 计时器在激活期间按键落下的判定就不会触发 主要起到这个作用
                self.timers['seed switch'].activate()
                self.seed_index += 1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]
                # print(self.selected_seed)

            # 交互区
            if keys[pygame.K_RETURN] and not self.timers['switch'].active:
                self.timers['switch'].activate()
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                if collided_interaction_sprite:
                    # 触发交互就不能动了
                    self.direction = pygame.math.Vector2()
                    if collided_interaction_sprite[0].name == 'Trader':
                        # toggle的意思是切换(这个方法是home里扔进来的)
                        self.toggle_shop()
                    elif collided_interaction_sprite[0].name == 'Fight':
                        self.toggle_fight()
                        self.fight = True
                    # 时间到了才能睡觉(18:00)
                    elif (480 + math.floor(self.timers['time'].pass_time() / 1000)) > 480:  # （完成测试后改成1080）
                        # 强制面朝左
                        self.status = 'left_idle'
                        self.sleep = True

    # 获得Sprite当前的状态
    def get_status(self):

        # 状态决定此时Sprite的动画包
        # 恢复待机状态
        if self.direction.magnitude() == 0:
            # 只保留第一个下划线之后的字符+‘_idle’
            self.status = self.status.split('_')[0] + '_idle'

        # 使用工具状态
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

        # 计时器跑完了直接睡觉
        if not self.timers['time'].active:
            self.sleep = True

    # 计时器刷新
    def update_timers(self):
        # 更新计时器
        for timer in self.timers.values():
            timer.update()

    # 碰撞检测(人物)
    def collision(self, direction):
        # 遍历碰撞组中的碰撞盒
        for sprite in self.collision_sprites.sprites():
            # hasattr  has attribute的缩写 检查是否有某种属性
            if hasattr(sprite, 'hitbox'):
                # pygame自带的矩形碰撞检测，返回True or False
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # 向右移动
                            # 把角色右边缘重置到碰撞物的左边缘（原始的方法） 后面的同理
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # 向左移动
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:  # 向下移动
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # 向上移动
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    # 移动精灵 和 碰撞盒
    def move(self, dt):
        # 统一速度
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # 水平移动
        self.pre_x = self.pos.x
        self.pos.x += self.direction.x * self.speed * dt
        # 这里四舍五入可以减少一些偶然的bug（？）
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # 垂直移动
        self.pre_y = self.pos.y
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def get_move_x(self):
        return self.pos.x - self.pre_x

    def get_move_y(self):
        return self.pos.y - self.pre_y

    # 重写Sprite中的update方法 tip:所有每一帧需要刷新的动作都放在这里，每一帧跑一次，不写就没有
    def update(self, dt):
        self.watering.set_volume(volumes['action'])
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()

        # 跟移动图片有关的方法往往需要dt
        self.move(dt)
        self.animate(dt)
