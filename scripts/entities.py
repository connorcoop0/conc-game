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
        self.collisions = {'up': 0, 'down': 0, 'right': 0, 'left': 0}
        self.directional_input = {'up_down': 0, 'left_right': 0}
        self.last_direction = 1
        self.velocity = [0, 0]
        self.air_time = 0
        self.ground_time = 0
        self.player_jumped = False
        self.grabbing = False
        self.can_grab = False
        self.dashing = 0
        self.wavedash = False
        self.can_dash = True
        self.is_climbing = False
        self.climb_time = 0
        self.wall_sliding = False
        self.wall_jump = 0

    def rect(self):
        return pygame.FRect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    # Sets action for animation
    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.animation.frame = 0
    
    def update(self, tilemap, movement=(0, 0)):
        # Get correct animation frame
        self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
        # refresh collisions every frame besides down
        self.collisions = {'up': 0, 'down': 0, 'right': 0, 'left': 0}

        # basic movement
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        # left/right cillision handling
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = 1
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = 1
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
                    self.ground_time += 1
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
                self.ground_time = 0
                self.wavedash += 1
                self.can_dash = True
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
        if self.ground_time > 5:
            self.climb_time = 0
        # if player is grabbing and can grab then we begin climbing
        if self.grabbing and self.can_grab:
            self.climbing()
            self.is_climbing = True
        # otherwise gravity is enabled
        else:
            self.is_climbing = False
            self.velocity[1] = min(5, self.velocity[1] + 0.1)
            
        
        if self.dashing < 50 and self.ground_time >= 5:
            self.can_dash = True
            # self.can_climb = True # This will reset the players climb distance
        # curently this makes it so that you can dash infinitely 

        if self.air_time > 5:
            self.ground_time = 0

        if (self.collisions['left'] or self.collisions['right']) and not self.is_climbing and not self.ground_time:
            self.wall_sliding = True
            self.velocity[1] = min(1, self.velocity[1] + 0.1)
        else:
            self.wall_sliding = False
        

        if self.wall_jump:
            if self.velocity[0] > 0:
                self.velocity[0] = max(0, self.velocity[0] - 0.1)
            elif self.velocity[0] < 0:
                self.velocity[0] = min(0, self.velocity[0] + 0.1)
            else:
                self.wall_jump = 0
        
        

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

    # Put entity on screen
    def render(self, surf, offset=(0, 0)):
        if self.can_dash or self.dashing > 45:
            surf.blit(pygame.transform.flip(self.img, self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        else:
            tinted_img = self.img.copy()
            tinted_img.fill((180, 200, 255), special_flags=pygame.BLEND_MULT)
            surf.blit(pygame.transform.flip(tinted_img, self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        if self.climb_time > 50:
            tinted_img = self.img.copy()
            tinted_img.fill((255, 305 - self.climb_time, 305 - self.climb_time), special_flags=pygame.BLEND_MULT)
            surf.blit(pygame.transform.flip(tinted_img, self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        


class Player(PhysicsEntity):
    def __init__(self, game, e_type, pos, size):
        super().__init__(game, e_type, pos, size)

    def jump(self):
        if self.wall_sliding:
            self.velocity[0] = self.flip * 2 if self.flip else -2
            self.wall_jump = 1
            self.velocity[1] = -2
            self.player_jumped = True
            self.climb_time += 25 if self.climb_time < 175 else 0
        elif self.ground_time:
            self.velocity[1] = -3
            self.player_jumped = True
            return True  
        else:
            self.player_jumped = False
            return False
        
    # implements gravity after release allowing for a more variable jump height dependent on length of key hold
    def stop_jump(self):
        if self.velocity[1] < -1.5:
            self.velocity[1] = min(5, self.velocity[1] + 1)

    def dash(self):
        if self.can_dash and self.dashing < 45:
            self.ground_time = 0
            self.can_dash = False
            self.dashing = 60
            return True
        else:
            return False
    
    def climbing(self):
        # while you are climbing up your climb timer goes up (if it hits 200 you can no longer climb)
        self.climb_time += 0.5 if self.velocity[1] == -1 else 0.1
        if self.climb_time < 200:
            if self.dashing <= 50:
                self.velocity[1] = self.directional_input['up_down'] * 1
        else:
            self.velocity[1] = 1