# 作   者：许晨昊
# 开发日期：17/3/2023

import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']
    # 暂时不需要update方法


class SoilLayer:
    def __init__(self, all_sprites):

        # 创建精灵组
        # 初始化碰撞盒
        self.hit_rects = None
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        # 各种各样的土壤图片
        self.soil_surfs = import_folder_dict('../graphics/soil')
        # print(self.soil_surfs)

        # 初始化坐标
        self.grid = None
        # 生成坐标
        self.create_soil_grid()
        # 生成碰撞盒
        self.create_hit_rects()

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
                # 确定这次碰撞在哪个格子里
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                print('soil_tile watered')

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
