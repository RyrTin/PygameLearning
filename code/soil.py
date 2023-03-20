# 作   者：许晨昊
# 开发日期：17/3/2023

import pygame
from settings import *
from pytmx.util_pygame import load_pygame


class SoilLayer:
    def __init__(self, all_sprites):

        # 创建精灵组

        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        # 加载土壤图片
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')
        # 初始化坐标
        self.grid = None
        # 需求：
        # 检查是否为可种植区
        # 检查土壤是否被浇水
        self.create_soil_grid()

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        # tip:  // 的作用是整数除法
        # 这里要获得纵向，横向的方块数量
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        # tips: [] for A in B 是列表生成式
        # 这句话是意思是把一行里的瓦块都创建一个[]，再把每一行的所有[]放到一组[]里，最后抽象出一个方括号地图(用来存东西)。
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        # 根据map信息在可耕种的格子里填上‘F’
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
        # print(self.grid)

