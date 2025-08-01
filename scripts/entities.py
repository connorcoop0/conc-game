import pygame
import random
import math

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.directional_input = {'up_down': 0, 'left_right': 0}
        self.action = ''
        self.set_action('idle')
        self.air_time = 0
        self.flip = False
        self.anim_offset = (-3, -3)
        self.dashing = 0
        self.last_direction = 1
        self.wavedash = False
        self.player_jumped = False

    # Sets action for animation
    def set_action(self, action):
        if self.action != action:
            self.action = action

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def update(self, tilemap, movement=(0, 0)):
        # Grab correct animation frame
        self.animation = self.game.assets[self.type + '/' + self.action].copy()

        # refresh collisions every frame
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # basic movement
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        # left/right cillision handling
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        if not self.collisions['down']:
            self.air_time += 1

        # up/down collision handling
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                    self.air_time = 0
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        # Flip entity based on direction
        if movement[0] > 0:
            self.flip = False
            self.last_direction = 1
        elif movement[0] < 0:
            self. flip = True
            self.last_direction = -1
        print(self.air_time)
        
        # Dashing
        if self.dashing:
            self.dashing -= 1
            if self.dashing > 58:
                if not self.directional_input['left_right'] and not self.directional_input['up_down']:
                    self.velocity[0] = self.last_direction * 4
                else:
                    self.velocity[0] = self.directional_input['left_right'] * 4
                if self.directional_input['up_down']:
                    self.velocity[1] = self.directional_input['up_down'] * 4
                else:
                    self.velocity[1] = 0
            if self.dashing > 50 and self.player_jumped:
                self.wavedash = True
            if self.dashing  <= 50 and self.wavedash: 
                self.velocity[0] *= 0.9 if abs(self.velocity[0]) > 0.5 else 0
            elif self.dashing == 45 and not self.wavedash:
                self.velocity[0] = 0
                self.velocity[1] = 0
        
        if not self.dashing:
            self.wavedash = False
        self.player_jumped = False

        # Gravity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)


    # change animation based on movement
        if self.dashing > 45:
            self.set_action('dash')
        elif self.air_time > 4:
            self.set_action('jump')
        elif frame_movement [0] != 0:
            self.set_action('run')
        
        else:
            self.set_action('idle')
        self.img = self.animation.update()
        
        # Make y movement 0 on up/down collision
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        
    
    # Put entity on screen
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.img, 0 - self.flip, 0), (self.pos[0] + self.anim_offset[0] - offset[0], self.pos[1] + self.anim_offset[1] - offset[1]))
    
    def jump(self):
        if self.air_time < 7:
            self.velocity[1] = -3
            self.player_jumped = True
            return True
        else:
            self.player_jumped = False
            return False
    
    def dash(self):
        if self.dashing <= 0 or (self.wavedash and self.dashing < 45): # this is making it so wavedash gives u infinite dashe
            self.dashing = 60
            return True
        else:
            return False
    