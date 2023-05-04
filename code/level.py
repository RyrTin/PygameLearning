import pygame

from settings import *
from tile import Tile
from player import Player
from levelplayer import LevelPlayer
from support import *
from random import choice, randint
from confirm import Confirm
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from transition import Transition


class Level:
    def __init__(self):

        # 获得显示区域

        self.display_surface = pygame.display.get_surface()
        # 生成可视精灵组
        self.visible_sprites = YSortCameraGroup()
        # 生成碰撞精灵组
        self.obstacle_sprites = pygame.sprite.Group()

        # 攻击精灵组
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # 初始化玩家
        self.player = None
        # 创建地图
        self.create_map()

        # 交互界面
        self.ui = UI()
        # 渐变
        self.transition = Transition()
        # 粒子效果
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        # 界面激活
        self.active = True

        # 页面状态
        self.game_paused = False
        self.enter = True
        self.finish = False

        # 确认界面
        self.confirm = Confirm(self.player)

    # 创建地图
    def create_map(self):
        # 读取贴图文件信息
        layouts = {
            'boundary': import_csv_layout('../data/map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('../data/map/map_Grass.csv'),
            'object': import_csv_layout('../data/map/map_Objects.csv'),
            'entities': import_csv_layout('../data/map/map_Entities.csv')
        }
        # 读取贴图
        graphics = {
            'grass': import_folder('../graphics/Grass'),
            'objects': import_folder('../graphics/objects')
        }

        # 生成地图物品精灵
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        # 把点位信息转化为贴图位置信息
                        # x*64就是横坐标，纵坐标同理
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE
                        # 如果是别边界区，放入障碍组（tile创建的精灵都有碰撞盒）
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        # 如果是草，随机选择贴图，放入碰撞组，可视组，可攻击组
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile(
                                (x, y),
                                [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                                'grass',
                                random_grass_image)
                        # 如果是物品 ， 根据编号选择物品，
                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)

                        # 如果是实体
                        if style == 'entities':
                            # 如果值为394  读取信息创建角色
                            if col == '394':
                                self.player = LevelPlayer(
                                    (x, y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic)
                            # 其他值则创建怪物
                            else:
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'
                                # 自定义敌人精灵
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.visible_sprites, self.attackable_sprites, self.enemy_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_money,
                                )

    def toggle_active(self):
        self.active = not self.active

    def toggle_pause(self):
        self.player.game_paused = not self.player.game_paused

    def toggle_finish(self):
        self.finish = not self.finish

    def toggle_quit(self):
        self.player.quit = not self.player.quit

    def create_attack(self):

        # 创建攻击（放入可视精灵组 攻击精灵组） （碰撞盒呢?)
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    # 魔法
    def create_magic(self, style, strength, cost):

        # 创建魔法
        # 治疗魔法
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    # 消除攻击
    def destroy_attack(self):
        # 当前攻击（存在）
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    # 玩家攻击逻辑
    def player_attack_logic(self):
        # 如果攻击精灵（存在）
        if self.attack_sprites:
            # 对每个攻击精灵进行碰撞检测
            for attack_sprite in self.attack_sprites:
                # 创建碰撞精灵组
                # spritecollide方法会返回两个组中有碰撞的精灵
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)

                # 如果碰撞精灵存在
                if collision_sprites:
                    # print(collision_sprites)
                    for target_sprite in collision_sprites:
                        # 如果被碰撞精灵是草
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            # 播放叶子动画
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            # 目标精灵消除
                            target_sprite.kill()
                        else:
                            # 如果不是草，造成伤害
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    # 玩家受击
    def damage_player(self, amount, attack_type):
        # 如果玩家不在无敌帧（可攻击）
        if self.player.vulnerable:
            # 玩家扣血
            self.player.health -= amount
            # 切换为无敌帧
            self.player.vulnerable = False
            # 记录受击时间
            self.player.hurt_time = pygame.time.get_ticks()
            # 制造受击粒子动画，放入可视组
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    # 触发死亡粒子效果
    def trigger_death_particles(self, pos, particle_type):

        # 制造粒子动画，加入可视组
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    # 增加金币
    def add_money(self, amount):

        self.player.money += amount

    # 运行
    def run(self):

        if self.player.game_paused:
            self.confirm.display()
        else:
            # 绘制图像
            self.display_surface.fill(WATER_COLOR)
            self.visible_sprites.custom_draw(self.player)
            # 更新ui
            self.ui.display(self.player)
            # 更新精灵
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
            if not self.enemy_sprites:
                self.finish = True

        # 画面渐变
        if self.enter:
            if self.transition.fade_in and not self.transition.fade_out:
                self.transition.color = 0
                self.transition.fade_in = False
                self.transition.fade_out = True
                self.transition.speed *= -1
            if self.transition.fade_out and not self.transition.fade_in:
                self.transition.fadeout()

            if not self.transition.fade_out and not self.transition.fade_in:
                self.enter = not self.enter
                self.transition.color = 255
                self.transition.fade_in = True

        elif self.finish:
            if self.transition.fade_in and not self.transition.fade_out:
                self.transition.fadein()

            elif self.transition.fade_in and self.transition.fade_out:
                self.transition.fade_out = False
                self.transition.color = 255
                self.transition.speed *= -1
                self.toggle_quit()
                # print(self.finish)


# 重写精灵组（自定义绘制）
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # 初始设置
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # 创建地板
        self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    # 自定义绘图
    def custom_draw(self, player):

        # 获得位移量
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # 绘制位移后的地面
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # 按图层位置遍历精灵 完成遮挡关系:
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    # 更新敌人
    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if
                         hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
