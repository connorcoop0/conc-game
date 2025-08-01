import pygame
import os

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation():
    def __init__(self, game, images, start_frame=0, img_dur=5, loop=True):
        self.game = game
        self.images = list(images)
        self.frame = start_frame
        self.loop = loop
        self.img_dur = img_dur

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) 
            return self.images[self.frame//self.img_dur % len(self.images)]
        else:
            print("Implement non looping logic you moron")
    
    def copy(self):
        return self
