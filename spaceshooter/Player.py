import pygame
from . import constants
from os import path

class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bullets, player_image, bullet_image, missle_image):
        pygame.sprite.Sprite.__init__(self)
        ## scale the player img down
        self.image = pygame.transform.scale(player_image, (50, 38))
        self.image.set_colorkey(constants.BLACK)
        self.bullet_image = bullet_image
        self.missle_image = missle_image

        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = constants.WIDTH / 2
        self.rect.bottom = constants.HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 900
        self.last_shot = pygame.time.get_ticks()
        self.lives = 1
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

        self.move_delay = 500
        self.last_move = pygame.time.get_ticks()

        self.all_sprites = all_sprites
        self.bullets = bullets

    def update(self):
        ## time out for powerups
        if self.power >=2 and pygame.time.get_ticks() - self.power_time > constants.POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        ## unhide 
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = constants.WIDTH / 2
            self.rect.bottom = constants.HEIGHT - 30

        self.speedx = 0    ## makes the player static in the screen by default. 
        # then we have to check whether there is an event hanlding being done for the arrow keys being 
        ## pressed 

        ## will give back a list of the keys which happen to be pressed down at that moment
        keystate = pygame.key.get_pressed()     
        if keystate[pygame.K_LEFT]:
            self.move(-1)
        elif keystate[pygame.K_RIGHT]:
            self.move(1)

        #Fire weapons by holding spacebar

        #  Add autofire
        # if keystate[pygame.K_SPACE]:
        if keystate:
            self.shoot()

        ## check for the borders at the left and right
        if self.rect.right > constants.WIDTH:
            self.rect.right = constants.WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

    def shoot(self):
        ## to tell the bullet where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top, self.bullet_image)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery, self.bullet_image)
                bullet2 = Bullet(self.rect.right, self.rect.centery, self.bullet_image)
                self.all_sprites.add(bullet1)
                self.all_sprites.add(bullet2)
                self.bullets.add(bullet1)
                self.bullets.add(bullet2)

            """ MOAR POWAH """
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery, self.bullet_image)
                bullet2 = Bullet(self.rect.right, self.rect.centery, self.bullet_image)
                missile1 = Missile(self.rect.centerx, self.rect.top, self.missle_image) # Missile shoots from center of ship
                self.all_sprites.add(bullet1)
                self.all_sprites.add(bullet2)
                self.all_sprites.add(missile1)
                self.bullets.add(bullet1)
                self.bullets.add(bullet2)
                self.bullets.add(missile1)

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (constants.WIDTH / 2, constants.HEIGHT + 200)

    def move(self, direction):
        now = pygame.time.get_ticks()
        if now - self.last_move > self.move_delay:
            self.rect.centerx += direction * 5


## defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.bottom < 0:
            self.kill()

        ## now we need a way to shoot
        ## lets bind it to "spacebar".
        ## adding an event for it in Game loop


class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

