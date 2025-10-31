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
BG = (24, 30, 36)
MUTED = (180, 180, 180)
BTN_BG = (50, 58, 66)
BTN_BORDER = (140, 140, 140)
BTN_HOVER = (70, 80, 92)

""" Graphics Stuff """
icon_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", "cats.jpg"))
terrain_image = "floor.jpg"
player_image = "cats.jpg"
roof_image = "roof.jpg"
boss_image_path = "amongus.png"
background_image_path = "pixel-grass-ground-and-stone-blocks-pattern-cubic-pixel-game-background-8bit-gaming-interface-2d-technology-retro-wallpaper-or-backdrop-with-soil-2H5J94K.jpg"
obstacle_images_paths = [
    "cats.jpg",
    "obstacle.jpg",  # top-half hitbox
    "cats.jpg",
    "cats.jpg",  # hanging
    "cats.jpg"
]

pygame.init()

""" Screen & Fonts """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
font = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 36)
pygame.display.set_icon(icon_image)
pygame.display.set_caption("Evading PSCP")
clock = pygame.time.Clock()

""" Obstacle Pre-Set """
num_obstacles = 9999
obstacle_images = []
for path in obstacle_images_paths:
    image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", path)).convert_alpha()
    scaled_versions = {
        "small": pygame.transform.scale(image, (100, 100)),
        "medium": pygame.transform.scale(image, (100, 160)),
        "wide": pygame.transform.scale(image, (175, 125)),
        "hanging": pygame.transform.scale(image, (125, 330))
    }
    obstacle_images.append(scaled_versions)

""" Game States """
MENU = "MENU"
CONTROLS = "CONTROLS"
START_PROMPT = "START_PROMPT"
GAME = "GAME"
state = MENU

game_over = False
game_started = False
score = 0
boss_score_thresholds = [1000, 4000, 6000]
current_boss_index = 0
boss_active = False
boss = None

# ------------------------- Utilities -------------------------
def draw_center_text(text, font_obj, color, y):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surf, rect)
    return rect

def make_button(text, center_x, center_y, padding=(28, 14)):
    label = font.render(text, True, WHITE)
    lw, lh = label.get_size()
    w, h = lw + padding[0]*2, lh + padding[1]*2
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (center_x, center_y)
    def draw(mouse_pos):
        bg = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_BG
        pygame.draw.rect(screen, bg, rect, border_radius=12)
        pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=12)
        screen.blit(label, (rect.centerx - lw//2, rect.centery - lh//2))
    return rect, draw

# ------------------------- Classes -------------------------
class Player:
    def __init__(self, image_path, x, y):
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

    def handle_input(self, keys):
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

    def reset(self):
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.velocity = 0
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

    def create(self, surface):
        surface.blit(self.image_slide if self.sliding else self.image_normal, self.obstacle)

class Obstacle:
    def __init__(self, x, terrain_top):
        self.type = random.randint(0, 4)
        self.hanging = self.type == 2
        self.top_half_hitbox = self.type == 1
        self.speed = 600
        self.active = True
        self.reset(x, terrain_top)

    def reset(self, x, terrain_top):
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
        if not game_over and self.active and game_started:
            self.obstacle.x -= self.speed * dt
        if self.obstacle.right < 0:
            spawn_obstacle(self)

    def create(self, surface):
        surface.blit(self.image, self.obstacle)

    def hitbox(self):
        if self.top_half_hitbox:
            return pygame.Rect(self.obstacle.x, self.obstacle.y, self.obstacle.width, self.obstacle.height//2)
        return self.obstacle

class Roof:
    def __init__(self, image_path, x, y):
        original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.roof = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.speed = 600
        self.active = True

    def move(self, dt):
        if not game_over and self.active and game_started:
            for i in range(2):
                self.roof[i].x -= self.speed * dt
            if self.roof[0].right <= 0:
                self.roof[0].x = self.roof[1].right
            if self.roof[1].right <= 0:
                self.roof[1].x = self.roof[0].right

    def create(self, surface):
        for i in self.roof:
            surface.blit(self.texture, i)

    @property
    def bottom(self):
        return self.roof[0].bottom

class Terrain:
    def __init__(self, image_path, x, y):
        original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.terrain = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.active = True
        self.speed = 600

    def move(self, dt):
        if not game_over and self.active and game_started:
            for i in range(2):
                self.terrain[i].x -= self.speed * dt
            if self.terrain[0].right <= 0:
                self.terrain[0].x = self.terrain[1].right
            if self.terrain[1].right <= 0:
                self.terrain[1].x = self.terrain[0].right

    def create(self, surface):
        for i in self.terrain:
            surface.blit(self.texture, i)

    @property
    def top(self):
        return self.terrain[0].top

class Boss:
    def __init__(self, image_path, terrain_top):
        self.original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (150, 200))
        self.rect = self.image.get_rect(bottomright=(SCREEN_WIDTH - 50, terrain_top))
        self.max_hp = 10
        self.hp = self.max_hp
        self.active = True

    def create(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)

    def draw_health_bar(self, surface):
        if self.active:
            bar_width = 300
            bar_height = 30
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = 50
            
            pygame.draw.rect(surface, BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
            
            health_percentage = max(0, self.hp / self.max_hp)
            health_width = int(bar_width * health_percentage)
            
            if health_percentage > 0.5:
                bar_color = (int(255 * (1 - (health_percentage - 0.5) * 2)), 255, 0)
            else:
                bar_color = (255, int(255 * health_percentage * 2), 0)
            
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, health_width, bar_height))
            
            pygame.draw.rect(surface, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
            
            health_text = font_small.render(f"BOSS HP: {self.hp}/{self.max_hp}", True, WHITE)
            text_rect = health_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 25))
            surface.blit(health_text, text_rect)

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.active = False
            global boss_active
            boss_active = False

# ------------------------- Game Objects -------------------------
background_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", background_image_path)).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

above = Roof(roof_image, 0, -675)
base = Terrain(terrain_image, 0, 650)
player = Player(player_image, 100, base.top)

obstacles = []
x = 1100
for _ in range(num_obstacles):
    obstacles.append(Obstacle(x, base.top))
    x += random.randint(550, 700)

def spawn_obstacle(obs):
    obs.type = random.randint(0, 4)
    obs.hanging = obs.type == 2
    obs.top_half_hitbox = obs.type == 1
    farthest = max(ob.obstacle.right for ob in obstacles if ob is not obs)
    new_x = max(SCREEN_WIDTH, farthest) + random.randint(550, 700)
    obs.reset(new_x, base.top)

def reset_game():
    global game_over, game_started, score, current_boss_index, boss_active, boss
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
    current_boss_index = 0
    boss_active = False
    boss = None

# ------------------------- UI Buttons -------------------------
btn_start_rect, btn_start_draw = make_button("Start Game", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)
btn_controls_rect, btn_controls_draw = make_button("Controls", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)
btn_quit_rect, btn_quit_draw = make_button("Quit", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150)

btn_back_rect, btn_back_draw = make_button("Back", SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)

btn_restart_rect, btn_restart_draw = make_button("Restart", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)
btn_return_rect, btn_return_draw = make_button("Return to Menu", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120)

# ------------------------- Main Loop -------------------------
running = True
while running:
    dt = clock.tick(FPS)/1000
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == MENU:
                if btn_start_rect.collidepoint(mouse_pos):
                    state = START_PROMPT
                elif btn_controls_rect.collidepoint(mouse_pos):
                    state = CONTROLS
                elif btn_quit_rect.collidepoint(mouse_pos):
                    running = False
            elif state in [CONTROLS, START_PROMPT]:
                if btn_back_rect.collidepoint(mouse_pos):
                    state = MENU
            elif state == GAME:
                if game_over:
                    if btn_restart_rect.collidepoint(mouse_pos):
                        reset_game()
                        state = START_PROMPT
                    elif btn_return_rect.collidepoint(mouse_pos):
                        reset_game()
                        state = MENU

    screen.fill(BG)

    # ------------------------- MENU -------------------------
    if state == MENU:
        draw_center_text("Evading PSCP", font, WHITE, 150)
        btn_start_draw(mouse_pos)
        btn_controls_draw(mouse_pos)
        btn_quit_draw(mouse_pos)

    # ------------------------- CONTROLS -------------------------
    elif state == CONTROLS:
        draw_center_text("Controls", font, WHITE, 100)
        draw_center_text("Space - Jump", font_small, MUTED, 250)
        draw_center_text("S/Down - Slide", font_small, MUTED, 300)
        draw_center_text("F - Attack Boss", font_small, MUTED, 350)
        btn_back_draw(mouse_pos)

    # ------------------------- START PROMPT -------------------------
    elif state == START_PROMPT:
        screen.blit(background_image, (0, 0))
        above.create(screen)
        base.create(screen)
        player.create(screen)
        
        for obs in obstacles:
            if obs.obstacle.right > 0:
                obs.create(screen)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        draw_center_text("Press SPACE to Start!", font, WHITE, SCREEN_HEIGHT//2)
        btn_back_draw(mouse_pos)
        if keys[pygame.K_SPACE]:
            state = GAME

    # ------------------------- GAME -------------------------
    elif state == GAME:
        if game_started:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BG)
        
        if game_started and not game_over:
            score += dt*100

        if current_boss_index < len(boss_score_thresholds):
            if score >= boss_score_thresholds[current_boss_index] and not boss_active:
                boss = Boss(boss_image_path, base.top)
                boss_active = True
                current_boss_index += 1

        player.handle_input(keys)
        player.apply_gravity(base, dt)

        if game_started:
            above.create(screen)
            above.move(dt)
            base.create(screen)
            base.move(dt)
        
        player.create(screen)

        if game_started:
            for obs in obstacles:
                if obs.obstacle.right > 0:
                    obs.move(dt)
                    obs.create(screen)
                    if player.obstacle.colliderect(obs.hitbox()) and not game_over:
                        game_over = True
                        for ob in obstacles:
                            ob.active = False
                        base.active = False
                        player.collision = True

        if boss_active and boss is not None:
            boss.create(screen)
            boss.draw_health_bar(screen)
            if keys[pygame.K_f]:
                boss.hit()

        score_text = font.render(f"Score  : {str(int(score)).zfill(5)}", True, WHITE)
        screen.blit(score_text, (1050, 50))

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            draw_center_text("Game Over", font, WHITE, SCREEN_HEIGHT//2 - 80)
            draw_center_text(f"Score: {int(score)}", font_small, MUTED, SCREEN_HEIGHT//2 - 20)

            btn_restart_draw(mouse_pos)
            btn_return_draw(mouse_pos)

    pygame.display.flip()

pygame.quit()
