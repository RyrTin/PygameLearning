# 作   者：许晨昊
# 开发日期：9/3/2023
import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprite import *
from pytmx.util_pygame import load_pygame
from support import *


# 负责绘制所有精灵的类
class Level:
    def __init__(self):
        # tip:基本各种精灵组的创建都在这里
        self.player = None
        # 获取当前显示的Surface对象（这里应该是整个显示窗口？）（官网文档没有看懂，存疑）
        self.display_surface = pygame.display.get_surface()
        # 创建sprite的空容器all_sprites(这里使用对Group重写的CameraGroup)
        self.all_sprites = CameraGroup()
        # 创建树木精灵的空容器
        self.tree_sprites = pygame.sprite.Group()
        # 创建hitbox的空容器collision_sprite用于碰撞检测
        self.collision_sprite = pygame.sprite.Group()
        # 实例化各种精灵，精灵是整个程序的核心部分
        self.setup()
        self.overlay = Overlay(self.player)

    # 创建精灵和碰撞盒并持久保存
    def setup(self):
        # 把各种图层信息保存在方格里的地图
        tmx_data = load_pygame('../data/map.tmx')

        # 创建精灵通常需要传一个group参数，似乎是用来确定这个精灵在哪个group里，相当于一个分类
        # 房子
        # 从每个图层中获取相应的物品贴图和位置信息，并用通用精灵方式生成精灵和相应的碰撞盒
        # 注意先后顺序 即使在同一优先级 也有内部先后顺序，先建立的精灵依然在底部
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # 栅栏
        # 两个group就是把同一个精灵归到两个组里，并且碰撞组主要使用hitbox这个属性（猜测）
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprite])

        # 水
        water_frames = import_folder('../graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        # 树
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprite, self.tree_sprites], obj.name)
        # 野花
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprite])

        # 碰撞瓷砖 （tiled 软件生成的地图自带碰撞瓷砖）
        for x, y, sur in tmx_data.get_layer_by_name('Collision').tiles():
            # 不需要可视化，只要用一个空的surf 然后放进碰撞组就可以了
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprite)

        # 创建并设置精灵(all_sprite实体) (player调用的是sprite父类初始化方法）
        # player重写了sprites父类的方法，实例化以后会在group里添加一个精灵
        # 玩家
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprite,
                    tree_sprites=self.tree_sprites
                )

        # 地图
        Generic(
            pos=(0, 0),
            surf=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground']
        )

    def run(self, dt):
        # 填充背景（显示区域） (覆盖上一个大循环生成的所有画面，可以保证显示区域外都是黑屏，不然都是拖影，之前绘制的画面永远都在）
        self.display_surface.fill('black')
        # 绘制精灵组（all_sprite)到显示区域（surface)
        # self.all_sprites.draw(self.display_surface)
        # 以player为中心绘制所有的sprite，不会画出碰撞盒，这里的参数就是Camera中心的精灵
        self.all_sprites.custom_draw(self.player)
        # 刷新精灵组(文档找不到详细说明，个人理解：直接按顺序调用group中每个实例化的sprite中的update()）
        # 这里的update方法几乎都是重写的，一般都是根据动画帧找到下一帧来改变image属性，真正意义上的刷新画面是上面的custom_draw方法
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # 获取当前显示区域(surface很抽象，不好理解)
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
