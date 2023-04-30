# 作   者：许晨昊
# 开发日期：9/3/2023
import pygame
from data import *
from player import Player
from overlay import Overlay
from sprite import *
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
from settings import *
import time


# 负责绘制所有精灵的类
class Home:
    # 各类初始化（精灵需要先创建组，再创建个体）
    def __init__(self):
        # tip:基本各种精灵组的创建都在这里,任何精灵都要先建组，再实例化并分组
        # 这里实例化一个玩家用于保存后面的玩家精灵（其他精灵实例化以后都保存在精灵组里，没有名字，实例了但没有完全实例）
        self.game_paused = None
        self.player = None
        # 获取当前显示的Surface对象（这里应该是整个显示窗口？）（官网文档没有看懂，存疑）
        self.display_surface = pygame.display.get_surface()

        # 创建各种精灵组
        # 创建相机精灵族的空容器all_sprites(这里使用对Group重写的CameraGroup，相机导致实际位置与逻辑位置不重合，所以单独建组)
        self.all_sprites = CameraGroup()
        # 创建树木精灵的空容器
        self.tree_sprites = pygame.sprite.Group()
        # 创建hitbox的空容器collision_sprite用于碰撞检测
        self.collision_sprite = pygame.sprite.Group()
        # 创建交互精灵组
        self.interaction_sprites = pygame.sprite.Group()
        # 土壤层
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprite)
        # 实例化各种精灵，精灵是整个程序的核心部分,且必须放在所拥有的实参类被创造之后
        self.setup()
        # 需要player参数的初始化放在最后

        # 创建覆盖层(UI)
        self.overlay = Overlay(self.player)

        self.settings = Settings()
        # 过渡界面
        self.transition = Transition(self.reset, self.player)

        # 天空
        self.rain = Rain(self.all_sprites)
        # 默认不下雨
        self.raining = False
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # 商店
        self.menu = Menu(self.player, self.toggle_shop)
        self.shop_active = False

        # 启用计时器
        self.player.timers['time'].activate()

        # 音乐
        # 说实话有点难听- -，到时候换个素材包
        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(volumes['action'])
        # self.music_1 = pygame.mixer.Sound('../audio/music.mp3')
        # self.music_1.set_volume(0.3)
        # self.music_1.play(loops=-1)
        self.music = pygame.mixer.Sound('../audio/BGM.mp3')
        self.music.set_volume(volumes['bgm'])
        self.music.play(loops=-1)

        # 界面激活
        self.active = True

    # 实例化游戏开始时就有的精灵和碰撞盒
    def setup(self):
        # 把各种图层信息保存在方格里的地图
        tmx_data = load_pygame('../data/map.tmx')

        # 创建精灵通常需要传一个group参数，似乎是用来确定这个精灵在哪个group里，相当于一个分类
        # 所有精灵的第一个分组基本都是all_sprites(如果需要画出来话)
        # 房子
        # 从每个图层中获取相应的物品贴图和位置信息，并用通用精灵方式生成精灵和相应的碰撞盒
        # 注意先后顺序 即使在同一优先级 也有内部先后顺序，先建立的精灵依然在底部
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # 创建栅栏
        # 两个group就是把同一个精灵归到两个组里，并且碰撞组主要使用hitbox这个属性（猜测）
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprite])

        # 生成水
        water_frames = import_folder('../graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        # 生成树
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=[self.all_sprites, self.collision_sprite, self.tree_sprites],
                name=obj.name,
                # 这里实际上传了个方法进去而不是参数
                # 为什么不直接写在树的精灵里？ 个人理解是树精灵类包含于玩家类，而玩家类包含于lever类所以写在level里
                # 这样就能实现跨类的方法实现,理论上这个方法写到玩家类里也没有问题，在damage树的同时生效
                # 这样等于是把这个方法传到了最里面的tree的damage()方法里，从逻辑角度上最合理
                player_add=self.player_add
            )
        # 生成野花
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprite])

        # 生成碰撞瓷砖 （tiled 软件生成的地图自带碰撞瓷砖）
        for x, y, sur in tmx_data.get_layer_by_name('Collision').tiles():
            # 不需要可视化，只要用一个空的surf 然后放进碰撞组就可以了
            # Surface方法的参数为（宽，高）
            Generic((x * TILE_SIZE, y * TILE_SIZE - 24), pygame.Surface((TILE_SIZE, TILE_SIZE + 24)),
                    self.collision_sprite)

        # 生成玩家
        # 创建并设置精灵(all_sprite实体) (player调用的是sprite父类初始化方法）
        # player重写了sprites父类的方法，实例化以后会在group里添加一个精灵
        # 根据map找到玩家的位置并获得位置参数，然后生成玩家精灵
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprite,
                    tree_sprites=self.tree_sprites,
                    interaction=self.interaction_sprites,
                    soil_layer=self.soil_layer,
                    toggle_shop=self.toggle_shop
                )
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

        # 生成地图
        Generic(
            pos=(0, 0),
            surf=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground']
        )

    # 添加玩家物品
    def player_add(self, item):

        self.player.item_inventory[item] += 1
        self.success.play()

    # 打开商店
    def toggle_shop(self):

        self.shop_active = not self.shop_active

    # 打开设置
    def toggle_menu(self):
        self.game_paused = not self.game_paused

    # 切换活跃
    def toggle_active(self):
        self.active = not self.active

    def stop_time(self):
        self.player.timers['time'].stop()

    def restart_time(self):
        self.player.timers['time'].reactivate()

    # 重置
    def reset(self):
        # 更新植物
        self.soil_layer.update_plants()

        # 重置土壤
        self.soil_layer.remove_water()
        # 随机下雨（调整下雨概率）
        self.raining = randint(0, 10) > 7  # 这里会返回一个True or False
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()
        # 重置苹果树
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # 重置时间
        self.sky.start_color = [255, 255, 255]

    # 植物收获碰撞(这里为啥写在Level里？猜测因为plant_sprites在level里并没有创建，无法传递到player里面)
    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    # 添加到库存
                    self.player_add(plant.plant_type)
                    # 生成粒子效果
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, z=LAYERS['main'])
                    # 清除植物
                    plant.kill()
                    # 从网格信息中删除
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    # 游戏运行（主要就是跑一边各个精灵的update）
    def run(self, dt):
        # 绘图逻辑
        # dt保证了每个sprite刷新一次的时间相等，从而控制时间同步
        # 填充背景（显示区域） (覆盖上一个大循环生成的所有画面，可以保证显示区域外都是黑屏，不然都是拖影，之前绘制的画面永远都在）
        self.display_surface.fill('black')
        # 绘制这一帧的所有精灵，所以应当发生在所有精灵完成动作以后或者以前，具体看图层的遮盖关系
        # Q：这里为什么先绘制再更新？
        # A: 因为一些覆盖层的逻辑必须发生在精灵绘制以后（要么把覆盖层做成精灵，个人觉得这样更好）
        # 以player为中心绘制所有的sprite，不会画出碰撞盒，这里的参数就是Camera中心的精灵，blit还未更新画面，需要等main中的update
        self.all_sprites.custom_draw(self.player)

        # 更新逻辑
        # 绘制精灵组(all_sprite)到显示区域（surface),所有具有图形的精灵都在这个组里，所以跑update()是没有问题的
        # self.all_sprites.draw(self.display_surface)
        # 刷新精灵组(文档找不到详细说明，个人理解：直接按顺序调用group中每个实例化的sprite中的update())
        # 这里的update方法几乎都是重写的，一般都是根据动画帧找到下一帧来改变image属性，真正意义上的刷新画面是上面的custom_draw方法
        # 开商店暂停游戏(防止键盘输入)
        if self.shop_active:
            # 菜单是单独的图层，必须后于精灵绘制（除非做成精灵并设置优先级）
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            # 植物收获碰撞判定
            self.plant_collision()

        # 天气逻辑
        # 开商店下雨暂停
        if self.raining and not self.shop_active:
            self.rain.update()
        # 天色在下午2:00开始黯淡
        if self.player.timers['time'].pass_time()/1000 > 360:
            self.sky.display(dt)

        # 覆盖层
        self.overlay.display()

        # 最高优先级层，并且不受玩家影响，最后绘制所以一定在最上面
        # 玩家睡觉时调用过渡画面方法（reset也在这个里面跑）
        # 所有操作判定在sleep为true时锁死 所以只能看到过渡画面
        # ？这里会产生一个时间加速的bug(已通过修改timer解决)
        if self.player.sleep:
            self.transition.play()


# 重写一个精灵组（主要是为了添加一个模拟相机的绘制功能）
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # 获取当前显示区域(整个显示画面)，因为后面的blit是默认叠加在当前显示区域上的
        self.display_surface = pygame.display.get_surface()
        # 相机位移量
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # 为什么需要player 因为player是参照物，其他精灵需要根据player改变自己位置
        # 用两个参数确定Player和Camera中心的关系,即偏移量
        # x轴方向的位移量
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        # y轴方向的位移量
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        # 确定位移发生在绘制之前，所以角色在被绘制出来时实际上是位移之后的位置，所以角色被固定在了屏幕中心
        # 如果角色一直移动的话，这个位移量是非常大的，这也导致了所有精灵的实际位置与逻辑位置不重合
        for layer in LAYERS.values():
            # 如果一个图层的位置更靠下（centery更大），根据透视关系她应该遮挡上方的图层，需要排在后面绘制
            # 所以对同优先级的排序是实现透视关系的一个好的解决办法
            # 排序后，按顺序从底层图层开始画，遍历每一个优先级，然后遍历在这个优先级的所有精灵，找到自己的位置后刷新精灵
            # lambda 匿名函数用法：  lambda (参数） ： 方法
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    # 用偏移矩阵表示偏移后的位置
                    # 偏移矩阵初始化 复制当前需要位移的精灵的位置
                    offset_rect = sprite.rect.copy()
                    # 相对位移是相反的所以减去偏移量
                    offset_rect.center -= self.offset
                    # 刷新所有精灵位移后的图像
                    self.display_surface.blit(sprite.image, offset_rect)

                    # # 角色碰撞框判定
                    # if sprite == player:
                    #     # 绘制角色的贴图框
                    #     pygame.draw.rect(self.display_surface, 'red', offset_rect, 10)
                    #     # 获取角色当前碰撞盒位置和大小
                    #     hitbox_rect = player.hitbox.copy()
                    #     # Q:但是此时hitbox的位置和offset_rect不重合 为什么？运行过程中看起来hitbox和角色一直是重合的
                    #     # A:初步判断为draw的时候只是改变了精灵的视觉位置，实际上没有改变精灵的逻辑位置
                    #     # 更新碰撞盒位置 使两个框的中心重合
                    #     hitbox_rect.center = offset_rect.center
                    #     # # 绘制角色的碰撞框
                    #     pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     # 绘制角色的目标点
                    #     pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
