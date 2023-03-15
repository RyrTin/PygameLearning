# 作   者：许晨昊
# 开发日期：15/3/2023
import pygame
from os import walk


# 根据文件名导入文件
def import_folder(path):
    surface_list = []
    # walk函数的作用是在以top为根节点的目录树中游走，对树中的每个目录生成一个由(dir path, surnames, filenames)三项组成的三元组
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            # print(full_path)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

