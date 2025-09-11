import pygame
import random

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

class Obstacle_1 :
    def __init__(self, x, y) :
        """ Obstacle1 Settings (Need Working)"""
        self.obstacle_1 = pygame.Rect(x, y, 100 ,100)
        self.x = x
        self.color = RED
        self.speed = 5
        self.event = False
        self.passed_half = False

    def move(self) :
        """ Move Obstacle1 (Need Working)"""
        if not game_over :
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.event :
                self.event = True
            if self.event :
                self.obstacle_1.x -= self.speed
                return self.respawn()
        return None
    
    def respawn(self) :
        """ Respawn Obstacle1 (Need Working) """
        if self.obstacle_1.right < SCREEN_WIDTH // 2 and not self.passed_half :
            self.passed_half = True
            new_x = SCREEN_WIDTH + random.randint(200, 600)
            new_ob = Obstacle_1(new_x, self.obstacle_1.y)
            new_ob.event = self.event
            return new_ob
        return None
            
    def create(self, surface) :
        """ Create Obstacle1 (Need Working)"""
        pygame.draw.rect(surface, self.color, self.obstacle_1)

class Player :
    def __init__(self, image, x, y) :
        """ Player Settings (Need Working) """
        original_image = pygame.image.load(image).convert_alpha()
        self.player = pygame.transform.scale(original_image, (100, 100))
        self.player_rect = self.player.get_rect(midbottom=(x, y))
        self.velocity_y = 0
        self.gravity = 0.35
        self.jump_strength = -12
        self.on_ground = True

    def handle_input(self) :
        """ Input reciever (Done / Changable) """
        if not game_over :
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.on_ground :
                self.velocity_y = self.jump_strength
                self.on_ground = False

    def apply_gravity(self, terrain) :
        """ Add Jumping physics (Done / Changable) """
        if not game_over :
            self.velocity_y += self.gravity
            self.player_rect.y += self.velocity_y
            if self.player_rect.bottom >= terrain.top :
                self.player_rect.bottom = terrain.top
                self.velocity_y = 0
                self.on_ground = True

    def create(self, surface) :
        """ Create Player (Done / Changable) """
        surface.blit(self.player, self.player_rect)

class Terrain :
    def __init__(self, x, y) :
        """ Terrain Settings (Need Working) """
        self.terrain = pygame.Rect(x, y, 999999, 999999)
        self.color = GREEN

    def create(self, surface) :
        """ Create Terrain (Need Working) """
        pygame.draw.rect(surface, self.color, self.terrain)

player = Player("Graphics/amongus.png", 100, 475)
base = Terrain(-1000, 475)
obstacles = [Obstacle_1(1200, 375)]

game_over = False

""" Main Function (Need Working) """
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.handle_input()
    player.apply_gravity(base.terrain)

    screen.fill(WHITE)
    base.create(screen)
    player.create(screen)

    for obs in obstacles[:]:
        new_obs = obs.move()
        obs.create(screen)

        if new_obs:
            obstacles.append(new_obs)
        
        if obs.obstacle_1.right < 0 :
            obstacles.remove(obs)

        if player.player_rect.colliderect(obs.obstacle_1):
            game_over = True

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
