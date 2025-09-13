import pygame
import random

""" Basic Settings """
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 120

""" Colors """
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

""" Graphics Stuff """
icon_image = pygame.image.load("Graphics/cats.jpg")
terrain_image = "Graphics/floor.jpg"
player_image = "Graphics/cats.jpg"
roof_image = "Graphics/roof.jpg"
obstacle_images_paths = [
    "Graphics/cats.jpg",
    "Graphics/obstacle.jpg",  # top-half hitbox
    "Graphics/cats.jpg",
    "Graphics/cats.jpg",  # hanging
    "Graphics/cats.jpg"
]

pygame.init()

""" Screen Settings """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
font = pygame.font.Font(None, 60)
pygame.display.set_icon(icon_image)
pygame.display.set_caption("PSCP Rush Hour")
clock = pygame.time.Clock()

""" Obstacle Pre-Set Settings """
num_obstacles = 5
obstacle_images = []
for path in obstacle_images_paths :
    image = pygame.image.load(path).convert_alpha()
    scaled_versions = {
        "small" : pygame.transform.scale(image, (100, 100)),
        "medium" : pygame.transform.scale(image, (100, 160)),
        "wide" : pygame.transform.scale(image, (175, 125)),
        "hanging" :pygame.transform.scale(image, (125, 330))
    }
    obstacle_images.append(scaled_versions)

class Player :
    def __init__(self, image_path, x, y) :
        """ Player Settings """
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image_normal = pygame.transform.scale(self.original_image, (100, 200))
        self.sliding_height = 80
        self.image_slide = pygame.transform.scale(self.original_image, (175, self.sliding_height))
        self.start_x, self.start_y = x, y
        self.obstacle = self.image_normal.get_rect(midbottom=(x, y))
        self.normal_height = self.obstacle.height
        self.velocity = 0
        self.gravity = 2500
        self.jump_strength = -1100
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

    def handle_input(self, keys) :
        """ Input Receiver """
        global game_started
        if not game_over :
            if keys[pygame.K_SPACE] and self.on_ground and not self.sliding :
                self.velocity = self.jump_strength
                self.on_ground = False
                game_started = True

            if keys[pygame.K_s] or keys[pygame.K_DOWN] :
                if not self.sliding and self.on_ground :
                    self.sliding = True
                    self.obstacle.height = self.sliding_height
                    self.obstacle.bottom = base.terrain.top
            else :
                if self.sliding :
                    self.sliding = False
                    self.obstacle.height = self.normal_height
                    self.obstacle.bottom = base.terrain.top

    def apply_gravity(self, floor, dt) :
        """ Jumping physics """
        self.velocity += self.gravity * dt
        self.obstacle.y += self.velocity * dt

        if not self.falling :
            if self.obstacle.bottom >= floor.top :
                self.obstacle.bottom = floor.top
                self.velocity = 0
                self.on_ground = True

        if self.collision :
            self.velocity = -1200
            self.collision = False
            self.falling = True

        if self.obstacle.top > SCREEN_HEIGHT :
            self.velocity = 0

    def reset(self) :
        """ Reset player """
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.velocity = 0
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

    def create(self, surface) :
        """ Draw player """
        surface.blit(self.image_slide if self.sliding else self.image_normal, self.obstacle)

class Obstacle :
    def __init__(self, x, terrain_top) :
        """ Obstacle Settings """
        self.type = random.randint(0, 4)
        self.hanging = self.type == 2
        self.top_half_hitbox = self.type == 1
        self.speed = 600
        self.active = True
        self.reset(x, terrain_top)

    def reset(self, x, terrain_top) :
        """ Reset Obstacle """
        if self.type in [0, 1] :
            self.width, self.height = 100, 160
            self.image = obstacle_images[self.type]["medium"]
        elif self.type == 3 :
            self.width, self.height = 175, 125
            self.image = obstacle_images[self.type]["wide"]
        elif self.type == 2 :
            self.width, self.height = 100, 330
            self.image = obstacle_images[self.type]["hanging"]
        else :
            self.width, self.height = 100, 100
            self.image = obstacle_images[self.type]["small"]

        if self.hanging :
            self.obstacle = self.image.get_rect(midtop=(x, above.roof.bottom))
        else :
            self.obstacle = self.image.get_rect(midbottom=(x, terrain_top))

    def move(self, dt) :
        """ Move Obstacle """
        if not game_over and self.active and game_started :
            self.obstacle.x -= self.speed * dt

        if self.obstacle.right < 0 :
            self.type = random.randint(0, 4)
            self.hanging = self.type == 2
            self.top_half_hitbox = self.type == 1
            max_x = max(obs.obstacle.right for obs in obstacles)
            new_x = max(SCREEN_WIDTH, max_x) + random.randint(550, 700)
            self.reset(new_x, base.terrain.top)

    def create(self, surface) :
        """ Draw Obstacle """
        surface.blit(self.image, self.obstacle)

    def hitbox(self) :
        """ Obstacle Hitbox """
        if self.top_half_hitbox :
            return pygame.Rect(self.obstacle.x, self.obstacle.y, self.obstacle.width, self.obstacle.height // 2)
        return self.obstacle

class Roof :
    def __init__(self, image_path, x, y) :
        """ Roof Settings """
        original_image = pygame.image.load(image_path).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.roof = self.texture.get_rect(topleft=(x, y))

    def create(self, surface) :
        surface.blit(self.texture, self.roof)

class Terrain :
    def __init__(self, image_path, x, y) :
        """ Terrain Settings """
        original_image = pygame.image.load(image_path).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH * 2, SCREEN_HEIGHT))
        self.terrain = self.texture.get_rect(topleft=(x, y))
        self.active = True
        self.speed = 600
 
    def move(self, dt) :
        """ Move Terrain """
        if not game_over and self.active and game_started :
            self.terrain.x -= self.speed * dt

        if self.terrain.right < SCREEN_WIDTH // 2 :
            self.reset(SCREEN_WIDTH, 650)

    def reset(self, x, terrain_topright) :
        self.terrain = self.texture.get_rect(topleft=(x, terrain_topright))

    def create(self, surface) :
        surface.blit(self.texture, self.terrain)

""" Game Settings """
above = Roof(roof_image, 0, -675)
base = Terrain(terrain_image, 0, 650)
player = Player(player_image, 100, base.terrain.top)
game_over = False
game_started = False
score = 0

obstacles = []
x = 1100
for _ in range(num_obstacles) :
    obstacles.append(Obstacle(x, base.terrain.top))
    x += random.randint(550, 700)

def reset_game() :
    """ Reset all game stats """
    global game_over, game_started, score
    player.reset()
    x = 1100
    for obs in obstacles :
        obs.type = random.randint(0, 4)
        obs.hanging = obs.type == 2
        obs.top_half_hitbox = obs.type == 1
        obs.reset(x, base.terrain.top)
        obs.active = True
        x += random.randint(550, 700)
    base.active = True
    random.shuffle(obstacles)
    game_over = False
    game_started = False
    score = 0

""" Main Attraction """
running = True
while running :
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()

    for event in pygame.event.get() :
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE] :
            running = False

    if game_started and not game_over :
        score += dt * 100

    if game_over and keys[pygame.K_r] :
        reset_game()

    player.handle_input(keys)
    player.apply_gravity(base.terrain, dt)

    screen.fill(WHITE)
    above.create(screen)
    base.create(screen)
    base.move(dt)
    player.create(screen)


    for obs in obstacles :
        if obs.obstacle.right > 0 :
            obs.move(dt)
            obs.create(screen)

            if player.obstacle.colliderect(obs.hitbox()) and not game_over :
                game_over = True
                for ob in obstacles :
                    ob.active = False
                base.active = False
                player.collision = True

    score_text = font.render(f"Score : {str(int(score)).zfill(5)}", True, WHITE)
    screen.blit(score_text, (1050, 50))

    pygame.display.flip()

pygame.quit()
