import pygame

""" Basic Settings (Done / Changable)"""
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 120

""" Colors """
WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (100,100,100)
RED = (220, 40, 40)
GREEN = (60,200,100)
BLUE = (80,140,220)
YELLOW = (240,220,60)
DARK = (20,20,30)

pygame.init()

""" Screen Settings (Done / Changable) """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
icon = pygame.image.load("Graphics/cats.jpg")
pygame.display.set_caption("PSCP Rush Hour")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

class Player :
    def __init__(self, image, x, y) :
        """ Player Settings (Need Working) """
        original_image = pygame.image.load(image).convert_alpha()
        self.player = pygame.transform.scale(original_image, (100, 100))
        self.player_rect = self.player.get_rect(midbottom=(x, y))
        self.velocity_y = 0
        self.gravity = 0.98
        self.jump_strength = -20
        self.on_ground = False

    def handle_input(self) :
        """ Input reciever (Done / Changable) """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.on_ground :
            self.velocity_y = self.jump_strength
            self.on_ground = False

    def apply_gravity(self, terrain) :
        """ Jumping physics (Done / Changable) """
        self.velocity_y += self.gravity
        self.player_rect.y += self.velocity_y
        if self.player_rect.bottom >= terrain.top :
            self.player_rect.bottom = terrain.top
            self.velocity_y = 0
            self.on_ground = True

    def appearance(self) :
        """ Create Player (Done / Changable) """
        screen.blit(self.player, self.player_rect)

class Terrain :
    def __init__(self, x, y) :
        """ Terrain Settings (Need Working) """
        self.terrain = pygame.Rect(x, y, 999999, 999999)
        self.color = GREEN

    def draw(self) :
        """ Create Terrain (Need Working) """
        pygame.draw.rect(screen, self.color, self.terrain)

player = Player("Graphics/amongus.png", 100, 475)
base = Terrain(-1000, 475)

""" Main Function (Need Working) """
running = True
while running :
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False

    player.handle_input()
    player.apply_gravity(base.terrain)

    screen.fill(WHITE)
    base.draw()
    player.appearance()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
