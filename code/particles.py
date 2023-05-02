import pygame
from support import import_folder
from random import choice


class AnimationPlayer:
    def __init__(self):
        # 导入动画帧
        self.frames = {
            # 魔法帧图片
            'flame': import_folder('../graphics/particles/flame/frames'),
            'aura': import_folder('../graphics/particles/aura'),
            'heal': import_folder('../graphics/particles/heal/frames'),

            # 动画帧图片
            'claw': import_folder('../graphics/particles/claw'),
            'slash': import_folder('../graphics/particles/slash'),
            'sparkle': import_folder('../graphics/particles/sparkle'),
            'leaf_attack': import_folder('../graphics/particles/leaf_attack'),
            'thunder': import_folder('../graphics/particles/thunder'),

            # 怪物死亡粒子
            'squid': import_folder('../graphics/particles/smoke_orange'),
            'raccoon': import_folder('../graphics/particles/raccoon'),
            'spirit': import_folder('../graphics/particles/nova'),
            'bamboo': import_folder('../graphics/particles/bamboo'),

            # 树叶粒子
            'leaf': (
                import_folder('../graphics/particles/leaf1'),
                import_folder('../graphics/particles/leaf2'),
                import_folder('../graphics/particles/leaf3'),
                import_folder('../graphics/particles/leaf4'),
                import_folder('../graphics/particles/leaf5'),
                import_folder('../graphics/particles/leaf6'),
                self.reflect_images(import_folder('../graphics/particles/leaf1')),
                self.reflect_images(import_folder('../graphics/particles/leaf2')),
                self.reflect_images(import_folder('../graphics/particles/leaf3')),
                self.reflect_images(import_folder('../graphics/particles/leaf4')),
                self.reflect_images(import_folder('../graphics/particles/leaf5')),
                self.reflect_images(import_folder('../graphics/particles/leaf6'))
            )
        }

    # 创建翻转帧列表
    def reflect_images(self, frames):
        new_frames = []

        for frame in frames:
            # flip方法可以翻转图片
            flipped_frame = pygame.transform.flip(frame, True, False)
            # 将翻转帧插入列表
            new_frames.append(flipped_frame)
        return new_frames

    # 创建草地粒子　放进组里
    def create_grass_particles(self, pos, groups):
        animation_frames = choice(self.frames['leaf'])
        # 生成粒子
        ParticleEffect(pos, animation_frames, groups)

    # 创建粒子　放进组里
    def create_particles(self, animation_type, pos, groups):
        # 根据动画类型选择动画帧
        animation_frames = self.frames[animation_type]
        # 生成粒子
        ParticleEffect(pos, animation_frames, groups)


# 生成粒子精灵
class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, animation_frames, groups):
        super().__init__(groups)
        # 精灵种类设置为魔法
        self.sprite_type = 'magic'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    # 播放动画
    def animate(self):
        self.frame_index += self.animation_speed
        # 播放帧到头了就删除自身
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        # 调用一次更新一次帧
        self.animate()
