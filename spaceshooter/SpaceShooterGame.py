from __future__ import division
import pygame
from pygame._sdl2.video import Window
import random
from os import path
import numpy as np


from . import constants
from .Player import *
from .Mob import *
from .Utils import *

img_dir = path.join(path.dirname(__file__), 'assets')

def sigmoid(x):
    sigmoid = 1.0/(1.0 + np.exp(-x))
    return sigmoid 

class SpaceShooterGame:
    def __init__(self, title, nn):
        self.screen_widht = constants.WIDTH
        self.screen_height = constants.HEIGHT
        self.title = title
        self.running = True
        self.game_over = False
        self.screen = None
        self.pause = True

        self.nn = nn

        self.img_dir = path.join(path.dirname(__file__), 'assets')
        self.sound_folder = path.join(path.dirname(__file__), 'sounds')

        self.font_name = pygame.font.match_font('arial')

        self.player = None

        self.img_dir = path.join(path.dirname(__file__), 'assets')
        self.player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png'))
        self.player_mini_img = pygame.transform.scale(self.player_img, (25, 19))
        self.player_mini_img.set_colorkey(constants.BLACK)
        self.bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png'))
        self.missile_img = pygame.image.load(path.join(img_dir, 'missile.png'))

        self.previous_steps = []
        self.regularization = 0.5

        
    def init_explosion_anim(self):
        self.explosion_anim = {}
        self.explosion_anim['lg'] = []
        self.explosion_anim['sm'] = []
        self.explosion_anim['player'] = []
        for i in range(9):
            filename = 'regularExplosion0{}.png'.format(i)
            img = pygame.image.load(path.join(img_dir, filename)).convert()
            img.set_colorkey(constants.BLACK)
            ## resize the explosion
            img_lg = pygame.transform.scale(img, (75, 75))
            self.explosion_anim['lg'].append(img_lg)
            img_sm = pygame.transform.scale(img, (32, 32))
            self.explosion_anim['sm'].append(img_sm)

            ## player explosion
            filename = 'sonicExplosion0{}.png'.format(i)
            img = pygame.image.load(path.join(img_dir, filename)).convert()
            img.set_colorkey(constants.BLACK)
            self.explosion_anim['player'].append(img)

    def init_powerups_imgs(self):
        self.powerup_images = {}
        self.powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
        self.powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

    def init_mobs_imgs(self):
        self.meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()
        self.meteor_images = []
        meteor_list = [
            'meteorBrown_big1.png',
            'meteorBrown_big2.png', 
            'meteorBrown_med1.png', 
            'meteorBrown_med3.png',
            'meteorBrown_small1.png',
            'meteorBrown_small2.png',
            'meteorBrown_tiny1.png'
        ]

        for image in meteor_list:
            self.meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())


    def create_mob(self, all_sprites, mobs):
        mob_element = Mob(meteor_images=self.meteor_images)
        all_sprites.add(mob_element)
        mobs.add(mob_element)

    def draw_text(self, text, size, x, y, color=constants.WHITE):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)       ## True denotes the font to be anti-aliased 
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_shield_bar(self, x, y, pct):

        pct = max(pct, 0) 

        fill = (pct / 100) * constants.BAR_LENGTH
        outline_rect = pygame.Rect(x, y, constants.BAR_LENGTH, constants.BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, constants.BAR_HEIGHT)
        pygame.draw.rect(self.screen, constants.GREEN, fill_rect)
        pygame.draw.rect(self.screen, constants.WHITE, outline_rect, 2)

    
    def draw_lives(self, x, y, lives, img):
        for i in range(lives):
            img_rect= img.get_rect()
            img_rect.x = x + 30 * i
            img_rect.y = y
            self.screen.blit(img, img_rect)

    def count_items_in_rect(self, rect, items):
        count = 0
        for item in items:
            if rect.colliderect(item):
                count += 1
        return count
    
    def set_game_over(self):
        elapsed_ticks = pygame.time.get_ticks() - self.survival_sec
        elapsed_seconds = elapsed_ticks // 1000

        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60

        self.result *= seconds // 10000

        self.screen.fill(constants.BLACK)
        self.draw_text("GAME OVER!", 40, constants.WIDTH/2, constants.HEIGHT/2)
        self.draw_text(f'Time: {minutes:02}:{seconds:02}'.upper(), 40, constants.WIDTH/2, constants.HEIGHT/2 + 40)
        
        pygame.display.update()
    
    def set_pause(self):
        self.screen.fill(constants.BLACK)
        self.draw_text("Pause...".upper(), 40, constants.WIDTH/2, constants.HEIGHT/2)
        pygame.display.update()

    def stop_pause(self):
        self.pause = False
    
    def make_move(self, predict):

        if predict[0] > random.random():
           decision = 1
        else:
           decision = -1

        self.player.move(decision)
        
        if 50 < self.player.rect.centerx < 430:
            self.result += 10
        else:
            self.result += 0.1

    def run_game(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_widht, self.screen_height))
        pygame.display.set_caption(self.title)

        clock = pygame.time.Clock()

        font_name = pygame.font.match_font('arial')
        self.player_img.convert()
        self.bullet_img.convert()
        self.missile_img.convert()


        self.init_explosion_anim()
        self.init_powerups_imgs()
        self.init_mobs_imgs()


        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        player = Player(all_sprites=all_sprites, bullets=bullets, player_image=self.player_img, bullet_image=self.bullet_img, missle_image=self.missile_img)
        self.player = player
        # Spawn {8} mobs
        for i in range(4):   
            self.create_mob(all_sprites, mobs)

        self.score = 0
        self.survival_sec = pygame.time.get_ticks()
        self.result = 0

            
        all_sprites.add(player)



        while self.running:
            
            if self.pause:
            # Pause the game until Esc is pressed
                self.set_pause()
                pygame.time.wait(1000)
                self.pause = False
            
            # Handle I/O
            clock.tick(constants.FPS)
            for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
                ## listening for the the X button at the top
                if event.type == pygame.QUIT:
                    self.running = False

                ## Press ESC to exit game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    # Press p for pause
                    if event.key == pygame.K_p:
                        self.pause = True
                ## event for shooting the bullets
                # elif event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_SPACE:
                #         player.shoot() 
            
            
            all_sprites.update()

            # Handle hits to mobs
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            ## now as we delete the mob element when we hit one with a bullet, we need to respawn them again
            ## as there will be no mob_elements left out 
            for hit in hits:
                self.score += 50 - hit.radius         ## give different scores for hitting big and small metoers
                m = Mob(meteor_images=self.meteor_images)
                all_sprites.add(m)
                mobs.add(m)
                expl = Explosion(hit.rect.center, 'lg', explosion_anim=self.explosion_anim)
                all_sprites.add(expl)
                if random.random() > 0.5:
                    pow = Pow(hit.rect.center, self.powerup_images)
                    all_sprites.add(pow)
                    powerups.add(pow)
                    # self.create_mob(all_sprites=all_sprites, mobs=mobs)      ## spawn a new mob
            
            # Handle player collision with mobs
            hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)        ## gives back a list, True makes the mob element disappear
            for hit in hits:
                player.shield -= hit.radius * 2
                expl = Explosion(hit.rect.center, 'sm', explosion_anim=self.explosion_anim)
                all_sprites.add(expl)
                self.create_mob(all_sprites, mobs)
                if player.shield <= 0: 
                    death_explosion = Explosion(player.rect.center, 'player', explosion_anim=self.explosion_anim)
                    all_sprites.add(death_explosion)
                    # running = False     ## GbackgrounAME OVER 3:D
                    player.hide()
                    player.lives -= 1
                    player.shield = 100


            # Handle player powerups
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'shield':
                    player.shield += random.randrange(10, 30)
                    if player.shield >= 100:
                        player.shield = 100
                if hit.type == 'gun':
                    player.powerup()




            ## if player died and the explosion has finished, end game
            if player.lives == 0:
                self.running = False
                self.game_over = True
                # self.quit()
                # pygame.display.update()

            self.screen.fill(constants.BLACK)

            all_sprites.draw(self.screen)
            self.draw_text(text=str(self.score), size=18, x=constants.WIDTH / 2, y=10, color=constants.WHITE)     ## 10px down from the screen
            self.draw_shield_bar(5, 5, player.shield)

            # Draw lives
            self.draw_lives(constants.WIDTH - 100, 5, player.lives, self.player_mini_img.convert())


            zone_width = 50

            middle_rect = pygame.Rect(player.rect.x, 200 , zone_width, constants.HEIGHT - 200)
            right_rect = pygame.Rect(player.rect.x + zone_width, 200, zone_width*2, constants.HEIGHT - 200)
            left_rect = pygame.Rect(player.rect.x - zone_width*2, 200, zone_width*2, constants.HEIGHT - 200)

            pygame.draw.rect(self.screen, (100, 100, 100), middle_rect, 1)
            pygame.draw.rect(self.screen, (100, 100, 100), right_rect, 1)
            pygame.draw.rect(self.screen, (100, 100, 100), left_rect, 1)


            left_mob_count = self.count_items_in_rect(left_rect, mobs)
            middle_mob_count = self.count_items_in_rect(middle_rect, mobs)
            right_mob_count = self.count_items_in_rect(right_rect, mobs)

            left_powerup_count = self.count_items_in_rect(left_rect, powerups)
            middle_powerup_count = self.count_items_in_rect(middle_rect, powerups)
            right_powerup_count = self.count_items_in_rect(right_rect, powerups)

            game_state_vector = [left_mob_count, 5 * left_powerup_count, middle_mob_count, -1 * middle_powerup_count, 5 * right_mob_count, right_powerup_count]
            predict = self.nn.activate(game_state_vector)

            self.make_move(predict)


            self.draw_text(str(left_mob_count), size=10, x=10, y=constants.HEIGHT // 2 , color=constants.RED)
            self.draw_text(str(middle_mob_count), size=10, x=middle_rect.x + 10, y=constants.HEIGHT // 2 , color=constants.RED)
            self.draw_text(str(right_mob_count), size=10, x=right_rect.x + 10, y=constants.HEIGHT // 2 , color=constants.RED)
            
            self.draw_text(str(left_powerup_count), size=10, x=10, y=constants.HEIGHT // 2 - 40 , color=constants.RED)
            self.draw_text(str(middle_powerup_count), size=10, x=middle_rect.x + 10, y=constants.HEIGHT // 2 - 40 , color=constants.RED)
            self.draw_text(str(right_powerup_count), size=10, x=right_rect.x + 10, y=constants.HEIGHT // 2 - 40 , color=constants.RED)

            ## Done after drawing everything to the screen
            pygame.display.flip()  

        if self.game_over:
        # Pause the game until Esc is pressed
            self.set_game_over()
            pygame.time.wait(2000)
            pygame.quit()
