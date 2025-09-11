import pygame
import random

""" Basic Settings (Done / Changable)"""
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 120

""" Colors """
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 40, 40)
GREEN = (60, 200, 100)
YELLOW = (240, 220, 60)

pygame.init()

""" Screen Settings (Done / Changable) """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PSCP Rush Hour")
clock = pygame.time.Clock()

class Player :
    def __init__(self, image, x, y) :
        """ Player Settings (Need Working) """
        original_image = pygame.image.load(image).convert_alpha()
        self.start_x = x
        self.start_y = y
        self.player = pygame.transform.scale(original_image, (100, 100))
        self.obstacle = self.player.get_rect(midbottom=(x, y))
        self.velocity_y = 0
        self.gravity = 0.35
        self.jump_strength = -12
        self.on_ground = True

    def handle_input(self, keys) :
        """ Input reciever (Done / Changable) """
        if not game_over :
            if keys[pygame.K_SPACE] and self.on_ground :
                self.velocity_y = self.jump_strength
                self.on_ground = False

    def apply_gravity(self, terrain, dt) :
        """ Add Jumping physics (Done / Changable) """
        if not game_over :
            self.velocity_y += self.gravity * dt * FPS
            self.obstacle.y += self.velocity_y * dt * FPS
            if self.obstacle.bottom >= terrain.top :
                self.obstacle.bottom = terrain.top
                self.velocity_y = 0
                self.on_ground = True

    def reset(self) :
        """ Reset player position and movement (Done / Changable) """
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.velocity_y = 0
        self.on_ground = True

    def create(self, surface) :
        """ Create Player (Done / Changable) """
        surface.blit(self.player, self.obstacle)

class Obstacle :
    def __init__(self, x, terrain_top) :
        """ Obstacle Settings """
        self.width = random.randint(50, 120)
        self.height = random.randint(50, 120)
        self.obstacle = pygame.Rect(x, terrain_top - self.height, self.width, self.height)
        self.color = RED
        self.speed = 5
        self.active = True

    def move(self, dt) :
        """ Move Obstacle (Need Working)"""
        if not game_over and self.active :
            self.obstacle.x -= self.speed * dt * FPS

        if self.obstacle.right < 0 :
            self.obstacle.x = SCREEN_WIDTH + random.randint(300, 600)
            self.height = random.randint(50, 120)
            self.width = random.randint(50, 120)
            self.obstacle.size = (self.width, self.height)
            self.obstacle.bottom = base.terrain.top

    def create(self, surface) :
        """ Create Obstacle (Need Working)"""
        pygame.draw.rect(surface, self.color, self.obstacle)

class Terrain :
    def __init__(self, x, y) :
        """ Terrain Settings (Need Working) """
        self.terrain = pygame.Rect(x, y, 999999, 999999)
        self.color = GREEN

    def create(self, surface) :
        """ Create Terrain (Need Working) """
        pygame.draw.rect(surface, self.color, self.terrain)

""" Game Settings """
player = Player("Graphics/amongus.png", 100, 475)
base = Terrain(-1000, 475)
game_over = False

num_obstacles = 5
distance = 400
start_x = 1200

obstacles = []
for i in range(num_obstacles) :
    x = start_x + i * distance
    obstacles.append(Obstacle(x, base.terrain.top))
random.shuffle(obstacles)

def reset_game() :
    """ Reset all game stats (Need Working) """
    global game_over
    player.reset()
    for i, obs in enumerate(obstacles) :
        obs.obstacle.x = start_x + i * distance
        obs.active = True
    random.shuffle(obstacles)
    game_over = False

""" Main Function (Need Working) """
running = True
while running :
    dt = clock.get_time() / 1000
    keys = pygame.key.get_pressed()

    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False

    if game_over and keys[pygame.K_r] :
        reset_game()

    player.handle_input(keys)
    player.apply_gravity(base.terrain, dt)

    screen.fill(WHITE)
    base.create(screen)
    player.create(screen)

    for obs in obstacles :
        obs.move(dt)
        obs.create(screen)

        if player.obstacle.colliderect(obs.obstacle) :
            game_over = True
            for ob in obstacles :
                ob.active = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
