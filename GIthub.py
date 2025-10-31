import pygame
import random
import os 

""" Basic Settings """
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 120

""" Colors """
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

""" Graphics Stuff """
icon_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", "cats.jpg"))
terrain_image = "floor.jpg"
player_image = "cats.jpg"
roof_image = "roof.jpg"
boss_image_path = "amongus.png"
obstacle_images_paths = [
    "cats.jpg",
    "obstacle.jpg",  # top-half hitbox
    "cats.jpg",
    "cats.jpg",  # hanging
    "cats.jpg"
]

pygame.init()

""" Screen Settings """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
font = pygame.font.Font(None, 60)
pygame.display.set_icon(icon_image)
pygame.display.set_caption("Evading PSCP")
clock = pygame.time.Clock()

""" Obstacle Pre-Set Settings """
num_obstacles = 9999
obstacle_images = []
for path in obstacle_images_paths :
    image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", path)).convert_alpha()
    scaled_versions = {
        "small" : pygame.transform.scale(image, (100, 100)),
        "medium" : pygame.transform.scale(image, (100, 160)),
        "wide" : pygame.transform.scale(image, (175, 125)),
        "hanging" : pygame.transform.scale(image, (125, 330))
    }
    obstacle_images.append(scaled_versions)

class Player :
    def __init__(self, image_path, x, y) :
        self.original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
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
                    self.obstacle.bottom = base.top
            else :
                if self.sliding :
                    self.sliding = False
                    self.obstacle.height = self.normal_height
                    self.obstacle.bottom = base.top

    def apply_gravity(self, terrain, dt) :
        self.velocity += self.gravity * dt
        self.obstacle.y += self.velocity * dt

        if not self.falling :
            if self.obstacle.bottom >= terrain.top :
                self.obstacle.bottom = terrain.top
                self.velocity = 0
                self.on_ground = True

        if self.collision :
            self.velocity = -1200
            self.collision = False
            self.falling = True

        if self.obstacle.top > SCREEN_HEIGHT :
            self.velocity = 0

    def reset(self) :
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.velocity = 0
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

    def create(self, surface) :
        surface.blit(self.image_slide if self.sliding else self.image_normal, self.obstacle)

class Obstacle :
    def __init__(self, x, terrain_top) :
        self.type = random.randint(0, 4)
        self.hanging = self.type == 2
        self.top_half_hitbox = self.type == 1
        self.speed = 600
        self.active = True
        self.reset(x, terrain_top)

    def reset(self, x, terrain_top) :
        if self.type in [0, 1] :
            self.image = obstacle_images[self.type]["medium"]
        elif self.type == 3 :
            self.image = obstacle_images[self.type]["wide"]
        elif self.type == 2 :
            self.image = obstacle_images[self.type]["hanging"]
        else :
            self.image = obstacle_images[self.type]["small"]

        if self.hanging :
            self.obstacle = self.image.get_rect(midtop=(x, above.bottom))
        else :
            self.obstacle = self.image.get_rect(midbottom=(x, terrain_top))

    def move(self, dt) :
        if not game_over and self.active and game_started :
            self.obstacle.x -= self.speed * dt
        if self.obstacle.right < 0 :
            spawn_obstacle(self)

    def create(self, surface) :
        surface.blit(self.image, self.obstacle)

    def hitbox(self) :
        if self.top_half_hitbox :
            return pygame.Rect(self.obstacle.x, self.obstacle.y, self.obstacle.width, self.obstacle.height // 2)
        return self.obstacle

class Roof :
    def __init__(self, image_path, x, y) :
        original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.roof = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.speed = 600
        self.active = True

    def move(self, dt) :
        if not game_over and self.active and game_started :
            for i in range(2)  :
                self.roof[i].x -= self.speed * dt
            if self.roof[0].right <= 0 :
                self.roof[0].x = self.roof[1].right
            if self.roof[1].right <= 0 :
                self.roof[1].x = self.roof[0].right

    def create(self, surface) :
        for i in self.roof :
            surface.blit(self.texture, i)

    @property
    def bottom(self) :
        return self.roof[0].bottom

class Terrain :
    def __init__(self, image_path, x, y) :
        original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.terrain = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.active = True
        self.speed = 600

    def move(self, dt) :
        if not game_over and self.active and game_started :
            for i in range(2)  :
                self.terrain[i].x -= self.speed * dt
            if self.terrain[0].right <= 0 :
                self.terrain[0].x = self.terrain[1].right
            if self.terrain[1].right <= 0 :
                self.terrain[1].x = self.terrain[0].right

    def create(self, surface) :
        for i in self.terrain :
            surface.blit(self.texture, i)

    @property
    def top(self) :
        return self.terrain[0].top

class Boss:
    def __init__(self, image_path, terrain_top):
        self.original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (150, 200))
        self.rect = self.image.get_rect(bottomright=(SCREEN_WIDTH - 50, terrain_top))
        self.hp = 10
        self.active = True

    def create(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.active = False
            global boss_active
            boss_active = False

boss = None

""" Game Settings """
above = Roof(roof_image, 0, -675)
base = Terrain(terrain_image, 0, 650)
player = Player(player_image, 100, base.top)
game_over = False
game_started = False
score = 0
boss_score_thresholds = [2000, 4000, 6000]
current_boss_index = 0
boss_active = False

obstacles = []
x = 1100
for _ in range(num_obstacles) :
    obstacles.append(Obstacle(x, base.top))
    x += random.randint(550, 700)

def spawn_obstacle(obs) :
    obs.type = random.randint(0, 4)
    obs.hanging = obs.type == 2
    obs.top_half_hitbox = obs.type == 1
    farthest = max(ob.obstacle.right for ob in obstacles if ob is not obs)
    new_x = max(SCREEN_WIDTH, farthest) + random.randint(550, 700)
    obs.reset(new_x, base.top)

def reset_game() :
    global game_over, game_started, score, current_boss_index, boss_active, boss
    player.reset()
    x = 1100
    for obs in obstacles :
        obs.type = random.randint(0, 4)
        obs.hanging = obs.type == 2
        obs.top_half_hitbox = obs.type == 1
        obs.reset(x, base.top)
        obs.active = True
        x += random.randint(550, 700)
    base.active = True
    random.shuffle(obstacles)
    game_over = False
    game_started = False
    score = 0
    current_boss_index = 0
    boss_active = False
    boss = None

""" Main Attraction """
running = True
while running :
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()

    for event in pygame.event.get() :
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE] :
            running = False

    # Score update (หยุดถ้ามีบอส)
    if game_started and not game_over and not boss_active:
        score += dt * 100

    # Spawn boss
    if current_boss_index < len(boss_score_thresholds):
        if score >= boss_score_thresholds[current_boss_index] and not boss_active:
            boss = Boss(boss_image_path, base.top)
            boss_active = True
            current_boss_index += 1

    # Reset game
    if game_over and keys[pygame.K_r] :
        reset_game()

    player.handle_input(keys)
    player.apply_gravity(base, dt)

    screen.fill(WHITE)
    above.create(screen)
    above.move(dt)
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

    # Draw boss
    if boss_active and boss is not None:
        boss.create(screen)
        # Example hit (กลุ่มอื่นจะทำระบบยิง)
        if keys[pygame.K_f]:
            boss.hit()

    score_text = font.render(f"Score  : {str(int(score)).zfill(5)}", True, WHITE)
    screen.blit(score_text, (1050, 50))

    pygame.display.flip()

pygame.quit()
