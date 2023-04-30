# 作   者：许晨昊
# 开发日期：15/3/2023
from _csv import reader

import pygame
from os import walk
from data import *


# 根据文件名导入文件
def import_folder(path):
    # 图片表
    surface_list = []
    # walk函数的作用是在以top为根节点的目录树中游走，对树中的每个目录生成一个由(dir path, surnames, filenames)三项组成的三元组
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            # print(full_path)
            # 贴图在加载后用convert_alpha()统一格式
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list


def import_folder_dict(path):
    # 图片字典
    surface_dict = {}
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            img_surf = pygame.image.load(full_path).convert_alpha()
            # image.split('.')[0]获取文件名并在对应的键存入图片
            # 字典添加时使用中括号[]
            surface_dict[image.split('.')[0]] = img_surf

    return surface_dict


def import_folder_start(path):
    # 图片表
    surface_list = []
    # walk函数的作用是在以top为根节点的目录树中游走，对树中的每个目录生成一个由(dir path, surnames, filenames)三项组成的三元组

    for image in range(0, 82):
        full_path = path + '/' + str(image) + '.png'
        # print(full_path)
        # 贴图在加载后用convert_alpha()统一格式
        load = pygame.image.load(full_path).convert_alpha()
        image_surf = pygame.transform.scale(load, (SCREEN_WIDTH, SCREEN_HEIGHT))
        surface_list.append(image_surf)

    return surface_list


def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map
