from __future__ import division
import pygame
import random
from os import path
import numpy as np
import os
import shutil
from PIL import Image
import imageio


from . import constants
from .Player import *
from .Mob import *
from .Utils import *

img_dir = path.join(path.dirname(__file__), 'assets')

def sigmoid(x):
    sigmoid = 1.0/(1.0 + np.exp(-x))
    return sigmoid 

class SpaceShooterGame:
    def __init__(self, title, nn, record_gameplay=False):
        self.screen_widht = constants.WIDTH
        self.screen_height = constants.HEIGHT
        self.title = title
        self.running = True
        self.game_over = False
        self.screen = None
        self.pause = True

        self.nn = nn

        self.img_dir = path.join(path.dirname(__file__), 'assets')

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
        self.record_gameplay = record_gameplay
        self.frames = []
        
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
        player_position = self.player.rect.centerx
        predict = np.array(predict)

        # Adjust weights based on position
        weights = np.ones_like(predict)

        # Penalize movements towards borders
        if player_position < 150:

            self.result += 0.1
        if player_position > 280:

            self.result += 0.1
        else:
            self.result += 1


        # Recalculate probabilities with adjusted weights
        adjusted_output = predict * weights
        adjusted_output += 2 * np.random.rand(*adjusted_output.shape)
        adjusted_output = adjusted_output / np.sum(adjusted_output)  # Normalize again

        if adjusted_output[0] > adjusted_output[2]:
            decision = -1
        elif adjusted_output[2] > adjusted_output[0]:
            decision = 1


        self.player.move(decision)

    def run_game(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_widht, self.screen_height))
        pygame.display.set_caption(self.title)

        clock = pygame.time.Clock()

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
        player = Player( 
            all_sprites=all_sprites, 
            bullets=bullets, 
            player_image=self.player_img, 
            bullet_image=self.bullet_img, 
            missle_image=self.missile_img
        )
        self.player = player
        # Spawn {10} mobs
        for i in range(10):   
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

            self.screen.fill(constants.BLACK)

            all_sprites.draw(self.screen)
            self.draw_text(text=str(self.score), size=18, x=constants.WIDTH / 2, y=10, color=constants.WHITE)     ## 10px down from the screen
            self.draw_shield_bar(5, 5, player.shield)

            # Draw lives
            self.draw_lives(constants.WIDTH - 100, 5, player.lives, self.player_mini_img.convert())


            zone_width = 50

            middle_rect = pygame.Rect(player.rect.x, 0 , zone_width, constants.HEIGHT)
            right_rect = pygame.Rect(player.rect.x + zone_width, 0, 2*zone_width, constants.HEIGHT)
            left_rect = pygame.Rect(player.rect.x - 2*zone_width, 0, 2*zone_width, constants.HEIGHT)

            pygame.draw.rect(self.screen, (100, 100, 100), middle_rect, 1)
            pygame.draw.rect(self.screen, (100, 100, 100), right_rect, 1)
            pygame.draw.rect(self.screen, (100, 100, 100), left_rect, 1)


            left_mob_count = self.count_items_in_rect(left_rect, mobs)
            middle_mob_count = self.count_items_in_rect(middle_rect, mobs)
            right_mob_count = self.count_items_in_rect(right_rect, mobs)

            left_powerup_count = self.count_items_in_rect(left_rect, powerups)
            middle_powerup_count = self.count_items_in_rect(middle_rect, powerups)
            right_powerup_count = self.count_items_in_rect(right_rect, powerups)

            game_state_vector = [
                left_mob_count, 
                5 * left_powerup_count, middle_mob_count,
                -1 * middle_powerup_count,
                right_mob_count, 
                5 * right_powerup_count,
                self.player.shield
                ]
            predict = self.nn.activate(game_state_vector)

            self.make_move(predict)


            self.draw_text(str(left_mob_count), size=10, x=player.rect.x - 2*zone_width, y=constants.HEIGHT // 2 , color=constants.RED)
            self.draw_text(str(middle_mob_count), size=10, x=middle_rect.x + 10, y=constants.HEIGHT // 2 , color=constants.RED)
            self.draw_text(str(right_mob_count), size=10, x=right_rect.x + 10, y=constants.HEIGHT // 2 , color=constants.RED)
            
            self.draw_text(str(left_powerup_count), size=10, x=player.rect.x - 2*zone_width, y=constants.HEIGHT // 2 - 40 , color=constants.RED)
            self.draw_text(str(middle_powerup_count), size=10, x=middle_rect.x + 10, y=constants.HEIGHT // 2 - 40 , color=constants.RED)
            self.draw_text(str(right_powerup_count), size=10, x=right_rect.x + 10, y=constants.HEIGHT // 2 - 40 , color=constants.RED)

            ## Done after drawing everything to the screen
            pygame.display.flip()  

            if self.record_gameplay:
                frame = pygame.surfarray.array3d(self.screen)
                self.frames.append(frame)

        if self.game_over:
        # Pause the game until Esc is pressed
            self.set_game_over()
            pygame.time.wait(2000)
            pygame.quit()

        
    def frames_to_images(self):
        print('Transforming frames to images ...')
        if not os.path.exists('frames'):
            os.mkdir('frames')
        for i, frame in enumerate(self.frames):
            img = Image.fromarray(np.transpose(frame, (1, 0, 2)))
            img.save(f"frames/frame_{i}.png")
        print('All frames transformed to images')


    def images_to_gif(self):
        print('Transforming images to gif ...')
        png_dir = 'frames'
        images = []
        file_dir = sorted(os.listdir(png_dir), key=lambda x: int(x.split('_')[1][:-4]))
        for file_name in file_dir:
            if file_name.endswith('.png'):
                file_path = os.path.join(png_dir, file_name)
                images.append(imageio.imread(file_path))

        imageio.mimsave('gameplay.gif', images, fps=60, loop=0)
        print('GIF sucessfuly created')
        shutil.rmtree('frames')
