# (ทั้งไฟล์) ขยายจากโค้ดของคุณ — ใส่ไฟล์นี้แทนไฟล์เดิม
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
ASSET_DIR = os.path.join(os.path.dirname(__file__), "Asset")
icon_image = None
try:
    icon_image = pygame.image.load(os.path.join(ASSET_DIR, "cats.jpg"))
except Exception:
    icon_image = pygame.Surface((32, 32))
    icon_image.fill((255, 0, 0))

terrain_image = "floor.jpg"
player_image = "cats.jpg"
roof_image = "roof.jpg"
obstacle_images_paths = [
    "cats.jpg",
    "obstacle.jpg",  # top-half hitbox
    "cats.jpg",
    "cats.jpg",  # hanging
    "cats.jpg"
]

# extra assets for weapon
gun_image_path = "sniper.png"
bullet_image_path = "fish.png"

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
for path in obstacle_images_paths:
    try:
        image = pygame.image.load(os.path.join(ASSET_DIR, path)).convert_alpha()
    except Exception:
        image = pygame.Surface((100, 160), pygame.SRCALPHA)
        pygame.draw.rect(image, (200, 50, 50), image.get_rect())
    scaled_versions = {
        "small": pygame.transform.scale(image, (100, 100)),
        "medium": pygame.transform.scale(image, (100, 160)),
        "wide": pygame.transform.scale(image, (175, 125)),
        "hanging": pygame.transform.scale(image, (125, 330))
    }
    obstacle_images.append(scaled_versions)


class Player:
    def __init__(self, image_path, x, y):
        """ Player Settings """
        try:
            self.original_image = pygame.image.load(os.path.join(ASSET_DIR, image_path)).convert_alpha()
        except Exception:
            self.original_image = pygame.Surface((100, 200), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, (50, 120, 200), self.original_image.get_rect())
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

        # weapon state
        self.has_gun = False
        self.ammo = 0
        self.shoot_cooldown = 0.2  # seconds between shots
        self.shoot_timer = 0.0

    def handle_input(self, keys):
        """ Input Receiver """
        global game_started
        if not game_over:
            if keys[pygame.K_SPACE] and self.on_ground and not self.sliding:
                self.velocity = self.jump_strength
                self.on_ground = False
                game_started = True

            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                if not self.sliding and self.on_ground:
                    self.sliding = True
                    self.obstacle.height = self.sliding_height
                    self.obstacle.bottom = base.top
            else:
                if self.sliding:
                    self.sliding = False
                    self.obstacle.height = self.normal_height
                    self.obstacle.bottom = base.top

    def apply_gravity(self, terrain, dt):
        """ Jumping physics """
        self.velocity += self.gravity * dt
        self.obstacle.y += self.velocity * dt

        if not self.falling:
            if self.obstacle.bottom >= terrain.top:
                self.obstacle.bottom = terrain.top
                self.velocity = 0
                self.on_ground = True

        if self.collision:
            self.velocity = -1200
            self.collision = False
            self.falling = True

        if self.obstacle.top > SCREEN_HEIGHT:
            self.velocity = 0

        # update shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
            if self.shoot_timer < 0:
                self.shoot_timer = 0

    def reset(self):
        """ Reset player """
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.velocity = 0
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False
        # reset weapon
        self.has_gun = False
        self.ammo = 0
        self.shoot_timer = 0.0

    def create(self, surface):
        """ Draw player """
        surface.blit(self.image_slide if self.sliding else self.image_normal, self.obstacle)


class Bullet:
    def __init__(self, x, y, speed=1500):
        self.speed = speed
        self.active = True
        # try load image
        try:
            img = pygame.image.load(os.path.join(ASSET_DIR, bullet_image_path)).convert_alpha()
            self.image = pygame.transform.scale(img, (30, 10))
        except Exception:
            self.image = pygame.Surface((30, 10), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 200, 0), self.image.get_rect())
        self.rect = self.image.get_rect(midleft=(x, y))
        self.lifetime = 2.0  # seconds
        self.age = 0.0

    def move(self, dt):
        if not self.active:
            return
        self.rect.x += int(self.speed * dt)
        self.age += dt
        if self.age >= self.lifetime or self.rect.left > SCREEN_WIDTH:
            self.active = False

    def create(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)


class GunPickup:
    def __init__(self, x, terrain_top):
        # try load image
        try:
            img = pygame.image.load(os.path.join(ASSET_DIR, gun_image_path)).convert_alpha()
            self.image = pygame.transform.scale(img, (60, 40))
        except Exception:
            self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (30, 200, 30), self.image.get_rect())
        self.rect = self.image.get_rect(midbottom=(x, terrain_top - 5))
        self.active = True
        self.speed = 600

    def move(self, dt):
        if not self.active:
            return
        if not game_over and game_started:
            self.rect.x -= int(self.speed * dt)
        if self.rect.right < 0:
            self.active = False

    def create(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)


class Obstacle:
    def __init__(self, x, terrain_top):
        """ Obstacle Settings """
        self.type = random.randint(0, 4)
        self.hanging = self.type == 2
        self.top_half_hitbox = self.type == 1
        self.speed = 600
        self.active = True
        self.reset(x, terrain_top)

    def reset(self, x, terrain_top):
        """ Reset Obstacle """
        if self.type in [0, 1]:
            self.image = obstacle_images[self.type]["medium"]
        elif self.type == 3:
            self.image = obstacle_images[self.type]["wide"]
        elif self.type == 2:
            self.image = obstacle_images[self.type]["hanging"]
        else:
            self.image = obstacle_images[self.type]["small"]

        if self.hanging:
            self.obstacle = self.image.get_rect(midtop=(x, above.bottom))
        else:
            self.obstacle = self.image.get_rect(midbottom=(x, terrain_top))

    def move(self, dt):
        """ Move Obstacle """
        if not game_over and self.active and game_started:
            self.obstacle.x -= self.speed * dt

        if self.obstacle.right < 0:
            spawn_obstacle(self)

    def create(self, surface):
        """ Draw Obstacle """
        if self.active:
            surface.blit(self.image, self.obstacle)

    def hitbox(self):
        """ Obstacle Hitbox """
        if self.top_half_hitbox:
            return pygame.Rect(self.obstacle.x, self.obstacle.y, self.obstacle.width, self.obstacle.height // 2)
        return self.obstacle


class Roof:
    def __init__(self, image_path, x, y):
        """ Roof Settings """
        try:
            original_image = pygame.image.load(os.path.join(ASSET_DIR, image_path)).convert_alpha()
        except Exception:
            original_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            original_image.fill((80, 80, 80))
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.roof = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.speed = 600
        self.active = True

    def move(self, dt):
        """ Move roofs """
        if not game_over and self.active and game_started:
            for i in range(2):
                self.roof[i].x -= self.speed * dt

            if self.roof[0].right <= 0:
                self.roof[0].x = self.roof[1].right
            if self.roof[1].right <= 0:
                self.roof[1].x = self.roof[0].right

    def create(self, surface):
        """ Draw both roofs """
        for i in self.roof:
            surface.blit(self.texture, i)

    @property
    def bottom(self):
        """ Return the bottom y of the roof """
        return self.roof[0].bottom


class Terrain:
    def __init__(self, image_path, x, y):
        """ Terrain Settings """
        try:
            original_image = pygame.image.load(os.path.join(ASSET_DIR, image_path)).convert_alpha()
        except Exception:
            original_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            original_image.fill((120, 85, 30))
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.terrain = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.active = True
        self.speed = 600

    def move(self, dt):
        """ Move both terrain """
        if not game_over and self.active and game_started:
            for i in range(2):
                self.terrain[i].x -= self.speed * dt

            if self.terrain[0].right <= 0:
                self.terrain[0].x = self.terrain[1].right
            if self.terrain[1].right <= 0:
                self.terrain[1].x = self.terrain[0].right

    def create(self, surface):
        """ Draw terrain """
        for i in self.terrain:
            surface.blit(self.texture, i)

    @property
    def top(self):
        """ Return the y of terrain top """
        return self.terrain[0].top


""" Game Settings """
above = Roof(roof_image, 0, -675)
base = Terrain(terrain_image, 0, 650)
player = Player(player_image, 100, base.top)
game_over = False
game_started = False
score = 0

obstacles = []
x = 1100
for _ in range(num_obstacles):
    obstacles.append(Obstacle(x, base.top))
    x += random.randint(550, 700)

# bullets and pickups
bullets = []
pickups = []
pickup_spawn_timer = 6.0  # seconds until next pickup spawn
pickup_timer = pickup_spawn_timer

def spawn_obstacle(obs):
    """ Spawn manager """
    obs.type = random.randint(0, 4)
    obs.hanging = obs.type == 2
    obs.top_half_hitbox = obs.type == 1
    farthest = max(ob.obstacle.right for ob in obstacles if ob is not obs)
    new_x = max(SCREEN_WIDTH, farthest) + random.randint(550, 700)
    obs.reset(new_x, base.top)
    obs.active = True

def spawn_pickup():
    # spawn somewhere off-right
    farthest = max(ob.obstacle.right for ob in obstacles)
    new_x = max(SCREEN_WIDTH, farthest) + random.randint(300, 800)
    gp = GunPickup(new_x, base.top)
    pickups.append(gp)

def reset_game():
    """ Reset all game stats """
    global game_over, game_started, score, pickup_timer, bullets, pickups
    player.reset()
    x = 1100
    for obs in obstacles:
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
    pickup_timer = pickup_spawn_timer
    bullets = []
    pickups = []

""" Main Attraction """
running = True
while running:
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False

    if game_started and not game_over:
        score += dt * 100

    if game_over and keys[pygame.K_r]:
        reset_game()

    # Player input & shooting
    player.handle_input(keys)
    # shoot with 'F'
    if keys[pygame.K_f] and player.has_gun and player.ammo > 0 and player.shoot_timer <= 0:
        # spawn bullet from mid-right of player
        bx = player.obstacle.right + 5
        by = player.obstacle.centery
        bullets.append(Bullet(bx, by))
        player.ammo -= 1
        player.shoot_timer = player.shoot_cooldown

    player.apply_gravity(base, dt)

    # update roof & terrain
    screen.fill(WHITE)
    above.create(screen)
    above.move(dt)
    base.create(screen)
    base.move(dt)
    player.create(screen)

    # move and draw pickups
    pickup_timer -= dt
    if pickup_timer <= 0:
        spawn_pickup()
        pickup_timer = pickup_spawn_timer + random.uniform(-2.0, 3.0)

    for pu in pickups:
        if pu.active:
            pu.move(dt)
            pu.create(screen)
            # pick up
            if player.obstacle.colliderect(pu.rect) and not game_over:
                pu.active = False
                player.has_gun = True
                player.ammo += 5  # give 5 bullets
    # cleanup pickups list occasionally
    pickups = [p for p in pickups if p.active]

    # obstacles
    for obs in obstacles:
        if obs.obstacle.right > 0 and obs.active:
            obs.move(dt)
            obs.create(screen)

            if player.obstacle.colliderect(obs.hitbox()) and not game_over:
                game_over = True
                for ob in obstacles:
                    ob.active = False
                base.active = False
                player.collision = True

    # bullets movement & collisions
    for b in bullets:
        if b.active:
            b.move(dt)
            b.create(screen)
            # check collision with obstacles
            for obs in obstacles:
                if obs.active and b.rect.colliderect(obs.hitbox()):
                    # destroy obstacle and bullet
                    obs.active = False
                    b.active = False
                    # optional: award score or small bonus
                    score += 200
                    # spawn chance to drop pickup from destroyed obstacle
                    if random.random() < 0.15:  # 15% chance
                        gp = GunPickup(obs.obstacle.right + random.randint(50,200), base.top)
                        pickups.append(gp)
                    break

    # cleanup bullets list
    bullets = [b for b in bullets if b.active]

     # display score and ammo
    score_text = font.render(f"Score  : {str(int(score)).zfill(5)}", True, WHITE)
    screen.blit(score_text, (1050, 50))

    # ammo UI
    ammo_text = font.render(f"Ammo : {player.ammo}", True, WHITE) if player.has_gun else font.render("Ammo : -", True, WHITE)
    screen.blit(ammo_text, (1050, 120))

    pygame.display.flip()

pygame.quit()
