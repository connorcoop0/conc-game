import pygame
import json

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
# This is for checking if there is a tile next to you that you can climb
CLIMB_OFFSETS = [(-1, 0), (1, 0)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
    
    def tiles_around(self, pos, tile_offset=NEIGHBOR_OFFSETS):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in tile_offset:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos, offset=(0,0)):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.FRect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size - offset[0], self.tile_size, self.tile_size - offset[0]))
        return rects
    
    def climb_rects_around(self, pos, offset=(0,0)):
        rects = []
        for tile in self.tiles_around(pos, CLIMB_OFFSETS):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.FRect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size - offset[0], self.tile_size, self.tile_size - offset[0]))
        return rects
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()
    
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def render(self, surf, offset=(0,0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))