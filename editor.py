import sys
import os
import pygame
from scripts.entities import Player
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.utils import Animation

RENDER_SCALE = 3.0

class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((1440, 810))
        self.display = pygame.Surface((480, 270))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        

        self.assets = {
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'decor': load_images('tiles/decor'),
            'large_decor': load_images('tiles/large_decor'),
            'spawners': load_images('tiles/spawners'),
        }

        self.tile_size = 16
        self.tilemap = Tilemap(self, self.tile_size)
        self.tilemap.load('map.json')
        self.movement = [0, 0]
        self.scroll = [0, 0]
        self.ongrid = True
        self.tile_type = 'grass'
        self.tile_variant = 0
        self.shift = False
        self.keys = list(self.assets.keys())
        self.tile_loc = 0
        self.clicking = False
        self.right_clicking = False

        
    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            # Camera movement
            self.scroll[0] += self.movement[0]
            self.scroll[1] += self.movement[1]

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            current_tile_image = self.assets[self.tile_type][self.tile_variant].copy()

            current_tile_image.set_alpha(100)
            

            self.tilemap.render(self.display, offset=self.scroll)
            self.display.blit(current_tile_image, (5, 5))
            if self.ongrid:
                self.display.blit(current_tile_image, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_image, mpos)
            

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_type, 'variant': self.tile_variant, 'pos': tile_pos}   

            if self.right_clicking and self.ongrid:
                if str(tile_pos[0]) + ';' + str(tile_pos[1]) in self.tilemap.tilemap:
                    self.tilemap.tilemap.pop(str(tile_pos[0]) + ';' + str(tile_pos[1]))
             
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.keys[self.tile_loc], 'variant': self.tile_variant, 'pos': (int(mpos[0] + self.scroll[0]), int(mpos[1] + self.scroll[1]))})
                    if event.button == 3:
                        self.right_clicking = True
                        if not self.ongrid:
                            for tile in self.tilemap.offgrid_tiles:
                                if (mpos[0] + self.scroll[0] >= tile['pos'][0] and mpos[0] + self.scroll[0] <= tile['pos'][0] + self.tile_size) and mpos[1] + self.scroll[1] >= tile['pos'][1] and mpos[1] + self.scroll[1] <= tile['pos'][1] + self.tile_size:
                                    self.tilemap.offgrid_tiles.remove(tile)
                    if event.button == 4:
                        if self.shift:
                            self.tile_variant = 0
                            self.tile_loc = (self.tile_loc + 1) % len(self.keys)
                            self.tile_type = self.keys[self.tile_loc]
                        else:
                            self.tile_variant = (self.tile_variant + 1) % len(os.listdir('data/images/tiles/'+self.tile_type))
                    if event.button == 5:
                        if self.shift:
                            self.tile_variant = 0
                            self.tile_loc = (self.tile_loc - 1) % len(self.keys)
                            self.tile_type = self.keys[self.tile_loc]
                        else:
                            self.tile_variant = (self.tile_variant - 1) % len(os.listdir('data/images/tiles/'+self.tile_type))
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = -2
                    if event.key == pygame.K_d:
                        self.movement[0] = 2
                    if event.key == pygame.K_w:
                        self.movement[1] = -2
                    if event.key == pygame.K_s:
                        self.movement[1] = 2
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_z:
                        # pop from stack of recent changes and add it to its correct destintion
                        print("undo")
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = 0
                    if event.key == pygame.K_d:
                        self.movement[0] = 0
                    if event.key == pygame.K_w:
                        self.movement[1] = 0
                    if event.key == pygame.K_s:
                        self.movement[1] = 0
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Editor().run()