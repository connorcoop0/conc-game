import pygame
import random
import math

# This is for checking if there is a tile next to you that you can climb
CLIMB_OFFSETS = [(-1, 0), (1, 0)]

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        # Animation/player info variables
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.action = ''
        self.animation = self.game.assets[self.type + '/' + 'idle'].copy()
        self.set_action('idle')
        self.flip = False
        self.anim_offset = (-3, -3)

        # Movement variables
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.directional_input = {'up_down': 0, 'left_right': 0}
        self.last_direction = 1
        self.velocity = [0, 0]
        self.air_time = 0
        self.player_jumped = False
        self.grabbing = False
        self.can_grab = False
        self.dashing = 0
        self.wavedash = False
        self.can_dash = True
        self.is_climbing = False

    # Sets action for animation
    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation.frame = 0

    def rect(self):
        return pygame.FRect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def update(self, tilemap, movement=(0, 0)):
        # Get correct animation frame
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
                self.pos[1] = int(entity_rect.y)
        
        # Flip entity based on direction
        if movement[0] > 0:
            self.flip = False
            self.last_direction = 1
        elif movement[0] < 0:
            self. flip = True
            self.last_direction = -1
        
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
                self.wavedash += 1
            if self.dashing  <= 50: 
                if self.wavedash:
                    self.velocity[0] *= 0.95 if abs(self.velocity[0]) > 0.5 else 0
                else:
                    self.velocity[0] *= 0.6 if abs(self.velocity[0]) > 0.5 else 0
                if not self.is_climbing:
                    self.velocity[1] = min(4, self.velocity[1] + 0.1)
                else:
                    self.velocity[1] = 0

        if not self.dashing:
            self.wavedash = 0
        self.player_jumped = False

        # change animation based on movement
        if self.dashing > 45:
            self.set_action('dash')
        elif self.is_climbing:
            if self.velocity[1] != 0:
                self.set_action('climb')
            else:
                self.set_action('hold')
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


        # Climbing logic
        if tilemap.climb_rects_around(self.pos):
            for rect in tilemap.climb_rects_around(self.pos):
                # if the player is on the wall they can grab
                if (rect.right == self.rect().left or rect.left == self.rect().right):
                    self.can_grab = True
                else:
                    self.can_grab = False
        # if no rects detected we cant grab
        else:
            self.can_grab = False
        # if player is grabbing and can grab then we begin climbing
        if self.grabbing and self.can_grab:
            self.climbing()
            self.is_climbing = True
        # otherwise gravity is enabled
        else:
            self.velocity[1] = min(5, self.velocity[1] + 0.1)
            self.is_climbing = False

    # Put entity on screen
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.img, self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)

    def jump(self):
        if self.air_time < 5 or self.is_climbing:
            self.velocity[1] = -3
            self.player_jumped = True
            return True  
        else:
            self.player_jumped = False
            return False
        
    def stop_jump(self):
        if self.velocity[1] < -1.5:
            self.velocity[1] = min(5, self.velocity[1] + 1)
    
    def dash(self):
        if self.dashing <= 0:
            self.dashing = 60
            return True
        else:
            return False
    
    def climbing(self):
        if self.dashing <= 50:
            self.velocity[1] = self.directional_input['up_down'] * 1