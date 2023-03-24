# 作   者：许晨昊
# 开发日期：17/3/2023

import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice


# 土壤精灵
class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']


# 浇水的土壤精灵
class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']


# 植物精灵
class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        # 初始化

        self.plant_type = plant_type
        # 加载贴图
        self.frames = import_folder(f'../graphics/fruit/{plant_type}')
        self.soil = soil
        # 灌溉状态
        self.check_watered = check_watered

        # 植物生长属性
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        # 精灵初始化
        # 生长状态与图片对应
        self.image = self.frames[self.age]
        # 纵向偏移
        self.y_offset = -16 if plant_type == 'corn' else -8
        # 获得种下去的那块土壤的位置信息，加上纵向偏移就是植物的位置
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.z = LAYERS['ground plant']

    def grow(self):
        if self.check_watered(self.rect.center):
            # 生长
            self.age += self.grow_speed

            # 长大后拥有碰撞体积并提高图层优先级
            if int(self.age) > 0:
                self.z = LAYERS['main']
                # 碰撞盒只要有就会撞，所以不在init内定义，尽管这不符合规范
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)
                # 优化碰撞表现，调整碰撞盒体积
                self.hitbox.centery -= 20

            # 限制生长
            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))


# 土壤类
class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):

        # 创建精灵组
        # 初始化碰撞盒
        self.hit_rects = None

        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        # 初始化土壤精灵组 水精灵组 植物精灵组
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        # 各种各样的土壤图片
        self.soil_surfs = import_folder_dict('../graphics/soil')
        self.water_surfs = import_folder('../graphics/soil_water')
        # print(self.soil_surfs)

        # 初始化坐标
        self.grid = None
        # 生成坐标
        self.create_soil_grid()
        # 生成碰撞盒
        self.create_hit_rects()

        # 声音(音效素材依托答辩)
        self.hoe_sound = pygame.mixer.Sound('../audio/hoe.wav')
        self.hoe_sound.set_volume(0.1)

        self.plant_sound = pygame.mixer.Sound('../audio/plant.wav')
        self.plant_sound.set_volume(0.1)

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        # tip:  // 的作用是整数除法
        # 这里要获得纵向，横向的方块数量
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        # tips: [] for A in B 意思是生成一个列表
        # 这句话是意思是把一行里的瓦块都创建一个[]，再把每一行的所有[]放到一组[]里，最后抽象出一个方括号地图(用来存东西)。
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        # 根据map信息在可耕种的格子里填上‘F’
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
        # for row in self.grid:
        #     print(row)

    def create_hit_rects(self):
        self.hit_rects = []
        # enumerate函数将返回一个索引序列
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                # 为每个可种植的单元格创建碰撞矩阵
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                self.hoe_sound.play()

                # 确定这次碰撞在哪个格子里
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                # 如果可以种植，就添加一个'X'代表被开垦，并且生成土壤贴图
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    # 同时检测，如果下雨了，自动浇水
                    if self.raining:
                        self.water_all()

    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            # 碰撞检测
            if soil_sprite.rect.collidepoint(target_pos):
                # 整除可以获得对应的行列信息
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                # 添加土地状态信息
                self.grid[y][x].append('W')
                # 这个Print验证了一件事就是x和w会无限的被添加进去
                # print(self.grid[y][x])
                pos = soil_sprite.rect.topleft
                surf = choice(self.water_surfs)
                # 生成水精灵
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                # 已经开垦了但是没浇水
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    # 把行列信息转成位置信息
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    WaterTile((x, y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])

    def remove_water(self):
        # 在一个组里被删掉的精灵也会在其他组被删掉（其实是同一个）
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    # 这里全部移除掉了 不管有几个'w' 所以之前可以无限添加不是很严重的bug（谁没事一直浇水啊）
                    cell.remove('W')

    def check_water(self, pos):
        # 检查是否被浇水
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, target_pos, seed):
        # 检查碰撞
        has_planed = False
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):

                # 获得方块位置（整数信息）
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                # 检查并添加种植信息
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    self.plant_sound.play()
                    # 触发种植
                    Plant(seed,
                          [self.all_sprites, self.plant_sprites, self.collision_sprites],
                          soil_sprite,
                          self.check_water)
                    has_planed = True
        return has_planed

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        # 这步不知道要干啥，为什么要清空？ 实测注释掉也没什么影响（可能是不清空会叠好几层，到时候删除土地不方便）
        # 猜测土地是根据状态表建立的，状态表会时不时更新，土块图层也要随着土壤位置关系刷新，所以这里动态生成更稳定。
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    # 选择需要哪种土块（上下左右是否有土块会影响土块形状）
                    # 检查上方有无土块 下左右同理
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]

                    # 初始砖块
                    tile_type = 'o'

                    # all() 里面全部为true 则返回true
                    # 四边都有土块的土块
                    if all((t, r, b, l)):
                        tile_type = 'x'

                    # 只有水平方向有土块
                    # any() 中有一个ture 则返回tre
                    if l and not any((t, r, b)):
                        tile_type = 'r'
                    if r and not any((t, l, b)):
                        tile_type = 'l'
                    if r and l and not any((t, b)):
                        tile_type = 'lr'

                    # 只有垂直方向有土块
                    if t and not any((l, r, b)):
                        tile_type = 'b'
                    if b and not any((t, l, r)):
                        tile_type = 't'
                    if t and b and not any((l, r)):
                        tile_type = 'tb'

                    # 两个边有土块
                    if l and b and not any((t, r)):
                        tile_type = 'tr'
                    if r and b and not any((t, l)):
                        tile_type = 'tl'
                    if l and t and not any((b, r)):
                        tile_type = 'br'
                    if r and t and not any((b, l)):
                        tile_type = 'bl'

                    # 三个边有土块
                    if all((t, b, r)) and not l:
                        tile_type = 'tbr'
                    if all((t, b, l)) and not r:
                        tile_type = 'tbl'
                    if all((l, r, t)) and not b:
                        tile_type = 'lrb'
                    if all((l, r, b)) and not t:
                        tile_type = 'lrt'

                    # 创建这块土地，并放入all_sprite(用于绘制)和soil_sprites(用于碰撞检测)中
                    SoilTile(
                        pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
                        surf=self.soil_surfs[tile_type],
                        groups=[self.all_sprites, self.soil_sprites]
                    )
