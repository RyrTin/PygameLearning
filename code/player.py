# 作   者：许晨昊
# 开发日期：14/3/2023
import pygame
from settings import *
from support import *
from timer import Timer


# 负责初始化精灵的类
# 主要被level导包
# 重写sprite类
class Player(pygame.sprite.Sprite):
    # 初始化
    def __init__(self, pos, group):
        # 调用父类方法初始化
        super().__init__(group)

        # 导入动画素材包

        self.animations = None
        self.import_assets()

        # 角色初始状态为面朝下
        self.status = 'down_idle'
        self.frame_index = 0

        # 初始化精灵
        # 设置精灵图像
        self.image = self.animations[self.status][self.frame_index]
        # 填充精灵颜色
        # self.image.fill('green')
        # 设置精灵位置
        self.rect = self.image.get_rect(center=pos)

        # 移动属性：方向，位置，速度
        # 方向属性：使用一个2维向量保存移动方向
        self.direction = pygame.math.Vector2()
        # 位置属性
        self.pos = pygame.math.Vector2(self.rect.center)
        # 速度属性
        self.speed = 200

        # 计时器(这里用词典形式保存实例化的计时器）
        # 计时器是重要的时间控制工具，主要控制某个方法的持续时间或按键响应次数等
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200)
        }

        # 工具
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # 种子
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    # 暂时没用
    def use_tool(self):
        # print(self.selected_tool)
        pass

    def use_seed(self):
        pass

    # 导入素材
    def import_assets(self):

        # 动作组名称词典
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}
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
        self.image = self.animations[self.status][int(self.frame_index)]

    # 响应按键（大部分功能都必须由按键响应，是各类功能开始的部分）
    def input(self):
        keys = pygame.key.get_pressed()

        # 使用工具时无法移动
        if not self.timers['tool use'].active:
            # 控制方向
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # 控制工具
            if keys[pygame.K_SPACE]:
                # 这里按下空格后activate持续了350ms
                self.timers['tool use'].activate()
                # 使用工具时不能移动，所以初始化速度（即位移变为0，0）
                self.direction = pygame.math.Vector2()
                # 重置动画帧
                self.frame_index = 0
            # 切换工具(按Q 并且还未激活计时器)
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                # 计时器在激活期间按键落下的判定就不会触发 主要起到这个作用
                self.timers['tool switch'].activate()
                self.tool_index += 1
                # 我的想法：self.tool_index = self.tool_index % 3 效果一样但是取余会慢
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]
            # 控制种子
            if keys[pygame.K_LCTRL]:
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

    # 计时器刷新
    def update_timers(self):
        # 更新计时器
        for timer in self.timers.values():
            timer.update()

    # 移动精灵
    def move(self, dt):
        # 统一速度
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # 水平移动
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x
        # 垂直移动
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    # 重写Sprite中的update方法
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()

        self.move(dt)
        self.animate(dt)
