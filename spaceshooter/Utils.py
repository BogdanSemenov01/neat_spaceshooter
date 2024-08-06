import pygame
import random
from . import constants
from os import path


# img_dir = path.join(path.dirname(__file__), 'assets')
# powerup_images = {}
# powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
# powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()


class Pow(pygame.sprite.Sprite):
    def __init__(self, center, powerup_images):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.top > constants.HEIGHT:
            self.kill()


# explosion_anim = {}
# explosion_anim['lg'] = []
# explosion_anim['sm'] = []
# explosion_anim['player'] = []
# for i in range(9):
#     filename = 'regularExplosion0{}.png'.format(i)
#     img = pygame.image.load(path.join(img_dir, filename)).convert()
#     img.set_colorkey(constants.BLACK)
#     ## resize the explosion
#     img_lg = pygame.transform.scale(img, (75, 75))
#     explosion_anim['lg'].append(img_lg)
#     img_sm = pygame.transform.scale(img, (32, 32))
#     explosion_anim['sm'].append(img_sm)

#     ## player explosion
#     filename = 'sonicExplosion0{}.png'.format(i)
#     img = pygame.image.load(path.join(img_dir, filename)).convert()
#     img.set_colorkey(constants.BLACK)
#     explosion_anim['player'].append(img)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size, explosion_anim):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75
        self.explosion_anim = explosion_anim

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

