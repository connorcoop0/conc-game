import sys
import pygame
from scripts.entities import Player
from scripts.utils import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.utils import Animation

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((1920, 1080))
        self.display = pygame.Surface((480, 270))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]

        self.assets = {
            'player/idle': Animation(self, load_images('entities/player/idle'), img_dur=10),
            'player/run': Animation(self, load_images('entities/player/run'), img_dur=6),
            'player/jump': Animation(self, load_images('entities/player/jump')),
            'player/dash': Animation(self, load_images('entities/player/dash')),
            'player/hold': Animation(self, load_images('entities/player/hold'), img_dur=10),
            'player/climb': Animation(self, load_images('entities/player/climb'), img_dur=10),
            'background': load_image('background.png'),
            'blocks': load_images('tiles/blocks')
        }

        self.player = Player(self, 'player', (50, 50), (8, 15))
        self.tilemap = Tilemap(self, 16)
        self.scroll = [0.0, 0.0]
        # for variable jump height
        self.jumping = 0

        
    def run(self):
        while True:
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 10
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 10
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            print(self.scroll)

            self.display.blit(self.assets['background'])
            self.tilemap.render(self.display, offset=render_scroll)
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player.directional_input['left_right'] -= 1
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.player.directional_input['left_right'] += 1
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_UP:
                        self.player.directional_input['up_down'] -= 1
                    if event.key == pygame.K_DOWN:
                        self.player.directional_input['up_down'] += 1
                    if event.key == pygame.K_c:
                        self.player.dash()
                    if event.key == pygame.K_x:
                        self.player.grabbing = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                        self.player.directional_input['left_right'] += 1
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                        self.player.directional_input['left_right'] -= 1
                    if event.key == pygame.K_SPACE:
                        self.player.stop_jump()
                    if event.key == pygame.K_UP:
                        self.player.directional_input['up_down'] += 1
                    if event.key == pygame.K_DOWN:
                        self.player.directional_input['up_down'] -= 1
                    if event.key == pygame.K_x:
                        self.player.grabbing = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()