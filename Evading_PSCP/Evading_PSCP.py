import pygame
import random
import os
import math

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
player_jump_image = "cats.jpg"  # Image for jumping state
player_slide_image = "cats.jpg"  # Image for sliding state
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

""" Game Settings """
MENU = "MENU"
CONTROLS = "CONTROLS"
START_PROMPT = "START_PROMPT"
GAME = "GAME"
state = MENU

game_over = False
game_started = False
prev_game_started = False
has_gun = True
slide_key_held = False 
ammo = 8 
max_ammo = 8
reloading = False
reload_time = 0
reload_duration = 2.0 
score = 0
boss_score_thresholds = [1000, 2300, 4200]
current_boss_index = 0
boss_active = False
boss_spawning = False 
boss = None
stage_text = None
stage_text_timer = 0
stage_text_duration = 2.0
boss_point_rewards = [300, 500, 700] 
obstacles_reset_after_boss = False 

# ------------------------- Utilities -------------------------

def line_segment_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    """Check if two line segments intersect using parametric form."""
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3
    
    denom = dx1 * dy2 - dy1 * dx2
    
    if abs(denom) < 0.0001:
        return False
    
    t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / denom
    u = ((x3 - x1) * dy1 - (y3 - y1) * dx1) / denom
    
    return 0 <= t <= 1 and 0 <= u <= 1

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
class StageText:
    def __init__(self, stage_num=None, custom_text=None):
        if custom_text:
            self.text = custom_text
        else:
            self.stage_num = stage_num
            self.text = f"Stage {stage_num}"
        self.x = -500
        self.target_x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed = 2000
        self.active = True
        self.display_timer = 0
        self.display_duration = 2.0
        
    def update(self, dt):
        if not self.active:
            return
            
        if self.x < self.target_x:
            self.x += self.speed * dt
            if self.x > self.target_x:
                self.x = self.target_x
        elif self.x == self.target_x:
            self.display_timer += dt
            if self.display_timer >= self.display_duration:
                self.target_x = SCREEN_WIDTH + 500
        else:
            self.x += self.speed * dt
            if self.x > SCREEN_WIDTH + 500:
                self.active = False
    
    def draw(self, surface):
        if not self.active:
            return
            
        stage_font = pygame.font.Font(None, 80)
        text_surf = stage_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        
        shadow_surf = stage_font.render(self.text, True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(self.x + 3, self.y + 3))
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)

class Player:
    def __init__(self, image_path, x, y, jump_image_path=None, slide_image_path=None):
        self.original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.normal_width = 100
        self.jumping_width = 130
        self.image_normal = pygame.transform.scale(self.original_image, (self.normal_width, 200))
        
        if jump_image_path:
            jump_img = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", jump_image_path)).convert_alpha()
            self.jumping_height = 180
            self.image_jump = pygame.transform.scale(jump_img, (self.jumping_width, self.jumping_height))
        else:
            self.jumping_height = 180
            self.image_jump = pygame.transform.scale(self.original_image, (self.jumping_width, self.jumping_height))
        
        if slide_image_path:
            slide_img = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", slide_image_path)).convert_alpha()
            self.sliding_height = 80
            self.image_slide = pygame.transform.scale(slide_img, (175, self.sliding_height))
        else:
            self.sliding_height = 80
            self.image_slide = pygame.transform.scale(self.original_image, (175, self.sliding_height))
        self.start_x, self.start_y = x, y
        self.obstacle = self.image_normal.get_rect(midbottom=(x, y))
        self.normal_height = 200
        self.velocity = 0
        self.gravity = 2500
        self.jump_strength = -1100
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False
        self.has_gun = False
        self.move_speed = 400

    def handle_input(self, keys, dt, boss_fight=False):
        global game_started, slide_key_held
        if not game_over:
            if boss_fight:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.obstacle.x -= self.move_speed * dt
                    self.obstacle.x = max(0, self.obstacle.x)
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.obstacle.x += self.move_speed * dt
                    self.obstacle.x = min(SCREEN_WIDTH - self.obstacle.width, self.obstacle.x)
                if slide_key_held and not self.sliding:
                    self.sliding = True
                    current_bottom = self.obstacle.bottom
                    current_centerx = self.obstacle.centerx
                    self.obstacle.height = self.sliding_height
                    self.obstacle.width = 17
                    self.obstacle.bottom = current_bottom
                    self.obstacle.centerx = current_centerx
                    if self.on_ground:
                        self.obstacle.bottom = base.top
                elif not slide_key_held and self.sliding:
                    self.sliding = False
                    current_bottom = self.obstacle.bottom
                    current_centerx = self.obstacle.centerx
                    if self.on_ground:
                        self.obstacle.height = self.normal_height
                        self.obstacle.width = self.normal_width
                        self.obstacle.bottom = base.top
                        self.obstacle.centerx = current_centerx
                    else:
                        self.obstacle.height = self.jumping_height
                        self.obstacle.width = self.jumping_width
                        self.obstacle.bottom = current_bottom
                        self.obstacle.centerx = current_centerx
            else:
                if slide_key_held and not self.sliding and self.on_ground:
                    self.sliding = True
                    self.obstacle.height = self.sliding_height
                    self.obstacle.bottom = base.top
                elif not slide_key_held and self.sliding and self.on_ground:
                    self.sliding = False
                    self.obstacle.height = self.normal_height
                    self.obstacle.bottom = base.top

    def apply_gravity(self, terrain, dt):
        self.velocity += self.gravity * dt
        self.obstacle.y += self.velocity * dt
        
        if not self.on_ground:
            if self.sliding:
                if self.obstacle.height != self.sliding_height or self.obstacle.width != 175:
                    current_bottom = self.obstacle.bottom
                    current_centerx = self.obstacle.centerx
                    self.obstacle.height = self.sliding_height
                    self.obstacle.width = 175
                    self.obstacle.bottom = current_bottom
                    self.obstacle.centerx = current_centerx
            else:
                if self.obstacle.height != self.jumping_height or self.obstacle.width != self.jumping_width:
                    current_bottom = self.obstacle.bottom
                    current_centerx = self.obstacle.centerx
                    self.obstacle.height = self.jumping_height
                    self.obstacle.width = self.jumping_width
                    self.obstacle.bottom = current_bottom
                    self.obstacle.centerx = current_centerx
        elif self.on_ground and not self.sliding and (self.obstacle.height != self.normal_height or self.obstacle.width != self.normal_width):
            current_bottom = self.obstacle.bottom
            current_centerx = self.obstacle.centerx
            self.obstacle.height = self.normal_height
            self.obstacle.width = self.normal_width
            self.obstacle.bottom = current_bottom
            self.obstacle.centerx = current_centerx
            
        if not self.falling:
            if self.obstacle.bottom >= terrain.top:
                self.obstacle.bottom = terrain.top
                self.velocity = 0
                self.on_ground = True
                if not self.sliding:
                    current_centerx = self.obstacle.centerx
                    self.obstacle.height = self.normal_height
                    self.obstacle.width = self.normal_width
                    self.obstacle.centerx = current_centerx
        if self.collision:
            self.velocity = -1200
            self.collision = False
            self.falling = True
        if self.obstacle.top > SCREEN_HEIGHT:
            self.velocity = 0

    def reset(self):
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.obstacle.width = self.normal_width
        self.obstacle.height = self.normal_height
        self.velocity = 0
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

    def create(self, surface):
        if self.sliding:
            image_to_blit = self.image_slide
        elif not self.on_ground:
            image_to_blit = self.image_jump
        else:
            image_to_blit = self.image_normal
        surface.blit(image_to_blit, self.obstacle)

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
        global boss_spawning, boss_active
        if boss_spawning or boss_active:
            if not game_over and self.active and game_started:
                if not boss_active:
                    self.obstacle.x -= self.speed * dt
            return
        
        if not game_over and self.active and game_started:
            self.obstacle.x -= self.speed * dt
                
        if self.obstacle.right < 0:
            if not boss_spawning and not boss_active:
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

class LaserWarning:
    """Preview/shadow showing where a laser will appear"""
    def __init__(self, start_x, start_y, target_x, target_y):
        self.start_pos = (start_x, start_y)
        self.target_pos = (target_x, target_y)
        self.width = 15
        self.age = 0
        self.warning_duration = 0.8
        
    def update(self, dt):
        self.age += dt
        
    def draw(self, surface):
        if self.age < self.warning_duration:
            alpha = int(128 + 127 * math.sin(self.age * 10))
            color = (255, 255, 0)
            
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            steps = 20
            dx = (self.target_pos[0] - self.start_pos[0]) / steps
            dy = (self.target_pos[1] - self.start_pos[1]) / steps
            for i in range(0, steps, 2):  
                start_idx = i
                end_idx = min(i + 1, steps)
                seg_start = (int(self.start_pos[0] + dx * start_idx), int(self.start_pos[1] + dy * start_idx))
                seg_end = (int(self.start_pos[0] + dx * end_idx), int(self.start_pos[1] + dy * end_idx))
                pygame.draw.line(temp_surface, (*color, alpha), seg_start, seg_end, self.width)
            
            surface.blit(temp_surface, (0, 0))
            
    def is_complete(self):
        return self.age >= self.warning_duration

class BossLaser(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__()
        self.start_pos = (start_x, start_y)
        self.target_pos = (target_x, target_y)
        self.width = 15
        self.color = (255, 0, 0)
        self.lifetime = 0.5
        self.age = 0
        
    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime:
            self.kill()
    
    def draw(self, surface):
        if self.age < self.lifetime:
            pygame.draw.line(surface, self.color, self.start_pos, self.target_pos, self.width)

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity_x, velocity_y):
        super().__init__()
        self.image = pygame.Surface((12, 12))
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        
    def update(self, dt):
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Boss:
    def __init__(self, image_path, terrain_top):
        self.original_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", image_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (250, 300))
        self.rect = self.image.get_rect(bottomright=(SCREEN_WIDTH - 50, terrain_top))
        self.max_hp = 10
        self.hp = self.max_hp
        self.active = True
        self.attack_timer = 0
        self.attack_cooldown = 2.0
        self.lasers = []
        self.laser_warnings = [] 
        self.bullets = pygame.sprite.Group()
        self.smg_burst_count = 0 
        self.smg_burst_delay = 0.1
        self.smg_timer = 0
        self.animation_timer = 0
        self.appearing = True
        self.appear_duration = 1.5
        self.start_x = SCREEN_WIDTH + 300
        self.target_x = SCREEN_WIDTH - 50
        self.current_x = self.start_x
        self.grace_period = 0.5
        self.grace_timer = 0
        self.warning_timer = 0
        self.warning_duration = 0.8 
        self.pending_attack = None 
        self.pending_laser_data = [] 

    def update(self, dt, player_rect):
        if not self.active:
            return
            
        if self.appearing:
            self.animation_timer += dt
            if self.animation_timer < self.appear_duration:
                # Slide in from right
                progress = self.animation_timer / self.appear_duration
                self.current_x = self.start_x - (self.start_x - self.target_x) * progress
                self.rect.right = self.current_x
            else:
                self.appearing = False
                self.animation_timer = 0
        
        if not self.appearing:
            if self.grace_timer < self.grace_period:
                self.grace_timer += dt
            else:
                if self.smg_burst_count > 0:
                    self.smg_timer += dt
                    if self.smg_timer >= self.smg_burst_delay:
                        self.smg_timer = 0
                        self.smg_burst_count -= 1
                        self.fire_smg_bullet(player_rect)
                elif self.pending_attack is not None:
                    self.warning_timer += dt
                    for warning in self.laser_warnings:
                        warning.age += dt
                    if self.warning_timer >= self.warning_duration:
                        self._execute_attack(player_rect)
                        self.pending_attack = None
                        self.warning_timer = 0
                        self.pending_laser_data = []
                else:
                    self.attack_timer += dt
                    if self.attack_timer >= self.attack_cooldown:
                        self.attack_timer = 0
                        self._start_attack(player_rect)
        
        self.bullets.update(dt)
        
    def fire_smg_bullet(self, player_rect):
        laser_start_x = self.rect.centerx
        laser_start_y = self.rect.top + 50  
        
        accuracy = 0.75 
        offset_x = random.uniform(-100, 100) * (1 - accuracy)
        offset_y = random.uniform(-100, 100) * (1 - accuracy)
        
        target_x = player_rect.centerx + offset_x
        target_y = player_rect.centery + offset_y
        
        dir_x = target_x - laser_start_x
        dir_y = target_y - laser_start_y
        dist = (dir_x**2 + dir_y**2)**0.5
        if dist > 0:
            speed = 500  # Moderate speed
            velocity_x = (dir_x / dist) * speed
            velocity_y = (dir_y / dist) * speed
            
            bullet = BossBullet(laser_start_x, laser_start_y, velocity_x, velocity_y)
            self.bullets.add(bullet)
    
    def _start_attack(self, player_rect):
        attack_type = random.choice(["smg", "barrage"])
        self.pending_attack = attack_type
        
        if attack_type == "barrage":
            self._create_laser_warnings(player_rect)
    
    def _create_laser_warnings(self, player_rect):
        barrage_count = 5
        base_accuracy = 0.6 
        
        for i in range(barrage_count):
            spread_angle = (i - barrage_count // 2) * 0.4 + random.uniform(-0.2, 0.2)
            
            dir_x = player_rect.centerx - self.rect.centerx
            dir_y = player_rect.centery - self.rect.centery
            dist = (dir_x**2 + dir_y**2)**0.5
            if dist > 0:
                dir_x /= dist
                dir_y /= dist
                
                offset_x = random.uniform(-0.3, 0.3) * (1 - base_accuracy)
                offset_y = random.uniform(-0.3, 0.3) * (1 - base_accuracy)
                dir_x += offset_x
                dir_y += offset_y
                
                new_dist = (dir_x**2 + dir_y**2)**0.5
                if new_dist > 0:
                    dir_x /= new_dist
                    dir_y /= new_dist
                
                cos_a = math.cos(spread_angle)
                sin_a = math.sin(spread_angle)
                rotated_x = dir_x * cos_a - dir_y * sin_a
                rotated_y = dir_x * sin_a + dir_y * cos_a
                
                target_dist = 2000
                target_x = self.rect.centerx + rotated_x * target_dist
                target_y = self.rect.centery + rotated_y * target_dist
                
                self.pending_laser_data.append({
                    'start': (self.rect.centerx, self.rect.centery),
                    'target': (target_x, target_y)
                })
                
                warning = LaserWarning(self.rect.centerx, self.rect.centery, target_x, target_y)
                self.laser_warnings.append(warning)
    
    def _execute_attack(self, player_rect):
        """Execute the attack after warning phase"""
        if self.pending_attack == "smg":
            self.smg_burst_count = random.randint(3, 5)
            self.smg_timer = 0
            self.fire_smg_bullet(player_rect)
        elif self.pending_attack == "barrage":
            for laser_data in self.pending_laser_data:
                laser = BossLaser(laser_data['start'][0], laser_data['start'][1], 
                                 laser_data['target'][0], laser_data['target'][1])
                self.lasers.append(laser)
            self.laser_warnings.clear()
            self.pending_laser_data = []
    
    def create(self, surface, dt):
        if self.active:
            surface.blit(self.image, self.rect)
            for warning in self.laser_warnings[:]:
                warning.draw(surface)
                if warning.is_complete():
                    self.laser_warnings.remove(warning)
            for laser in self.lasers[:]:
                laser.draw(surface)
                laser.update(dt)
                if laser.age >= laser.lifetime:
                    self.lasers.remove(laser)
            self.bullets.draw(surface)

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

    def hit(self, player_ref=None, obstacles_ref=None, base_ref=None):
        self.hp -= 2
        if self.hp <= 0:
            self.active = False
            global boss_active, stage_text, current_boss_index, score, boss_point_rewards, boss_spawning
            boss_active = False
            boss_spawning = False
            
            if current_boss_index > 0 and current_boss_index <= len(boss_point_rewards):
                score += boss_point_rewards[current_boss_index - 1]
            
            if current_boss_index == 3:
                stage_text = StageText(custom_text="Endless")
            elif current_boss_index <= 2:
                stage_text = StageText(current_boss_index + 1)
            
            if player_ref is not None:
                player_ref.reset()
            
            if obstacles_ref is not None and base_ref is not None:
                x = 1100
                for obs in obstacles_ref:
                    obs.active = True
                    obs.type = random.randint(0, 4)
                    obs.hanging = obs.type == 2
                    obs.top_half_hitbox = obs.type == 1
                    obs.reset(x, base_ref.top)
                    x += random.randint(550, 700)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 8))
        self.image.fill((255, 230, 90))
        self.rect = self.image.get_rect(midleft=(x, y))
        self.speed = 1000

    def update(self, dt):
        self.rect.x += self.speed * dt
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

        pass

class Gunpickup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", "sniper.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 600

    def update(self, dt):
        global game_started
        if not game_over and game_started:
            self.rect.x -= self.speed * dt
            if self.rect.right < 0:
                self.kill()

# ------------------------- Game Objects -------------------------
background_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "Asset", background_image_path)).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

bullets = pygame.sprite.Group()
shoot_cooldown = 0.3
shoot_timer = 0
guns = pygame.sprite.Group()
gun_spawn_timer = 0
gun_spawn_interval = 6

above = Roof(roof_image, 0, -675)
base = Terrain(terrain_image, 0, 650)
player = Player(player_image, 100, base.top, player_jump_image, player_slide_image)

obstacles = []
x = 1100
for _ in range(num_obstacles):
    obstacles.append(Obstacle(x, base.top))
    x += random.randint(550, 700)

def spawn_obstacle(obs):
    global boss_spawning, boss_active
    if boss_spawning or boss_active:
        obs.active = False
        return
    obs.active = True
    obs.type = random.randint(0, 4)
    obs.hanging = obs.type == 2
    obs.top_half_hitbox = obs.type == 1
    farthest = SCREEN_WIDTH
    for ob in obstacles:
        if ob is not obs and ob.active:
            farthest = max(farthest, ob.obstacle.right)
    new_x = farthest + random.randint(550, 700)
    obs.reset(new_x, base.top)

def reset_game():
    global game_over, game_started, prev_game_started, score, current_boss_index, boss_active, boss, stage_text, ammo, boss_spawning, reloading, reload_time
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
    prev_game_started = False
    score = 0
    ammo = max_ammo 
    reloading = False
    reload_time = 0
    current_boss_index = 0
    boss_active = False
    boss_spawning = False
    boss = None
    stage_text = None

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
        elif event.type == pygame.KEYDOWN:
            if state == START_PROMPT and event.key == pygame.K_SPACE:
                state = GAME
                game_started = True
            elif state == GAME and not game_over:
                is_jump_key = (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP)
                
                if is_jump_key:
                    if not boss_active:
                        if player.on_ground and not player.sliding:
                            player.velocity = player.jump_strength
                            player.on_ground = False
                            game_started = True
                    elif boss_active:
                        if player.on_ground:
                            player.velocity = player.jump_strength
                            player.on_ground = False
                
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    slide_key_held = True
                    if not boss_active:
                        if player.on_ground and not player.sliding:
                            player.sliding = True
                            player.obstacle.height = player.sliding_height
                            player.obstacle.bottom = base.top
                    elif boss_active:
                        if not player.sliding:
                            player.sliding = True
                            current_bottom = player.obstacle.bottom
                            current_centerx = player.obstacle.centerx
                            player.obstacle.height = player.sliding_height
                            player.obstacle.width = 175
                            player.obstacle.bottom = current_bottom
                            player.obstacle.centerx = current_centerx
                            if player.on_ground:
                                player.obstacle.bottom = base.top
        elif event.type == pygame.KEYUP:
            if state == GAME and not game_over:
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    slide_key_held = False
                    if player.sliding:
                        if not boss_active and player.on_ground:
                            player.sliding = False
                            player.obstacle.height = player.normal_height
                            player.obstacle.bottom = base.top
                        elif boss_active:
                            player.sliding = False
                            current_bottom = player.obstacle.bottom
                            current_centerx = player.obstacle.centerx
                            if player.on_ground:
                                player.obstacle.height = player.normal_height
                                player.obstacle.width = player.normal_width
                                player.obstacle.bottom = base.top
                                player.obstacle.centerx = current_centerx
                            else:
                                player.obstacle.height = player.jumping_height
                                player.obstacle.width = player.jumping_width
                                player.obstacle.bottom = current_bottom
                                player.obstacle.centerx = current_centerx
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
        draw_center_text("W / Space / Up - Jump", font_small, MUTED, 250)
        draw_center_text("S / Down - Slide ", font_small, MUTED, 300)
        draw_center_text("F - Attack Boss", font_small, MUTED, 350)
        draw_center_text("A / D or Left / Right - Move",  font_small, MUTED, 400)
        draw_center_text("(Can only slide while jumping and use A / D to move during boss fight)", font_small, MUTED, 550)
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

    # ------------------------- GAME -------------------------
    elif state == GAME:
        if game_started and not prev_game_started:
            stage_text = StageText(1)
        prev_game_started = game_started

        if stage_text is not None:
            stage_text.update(dt)
            if not stage_text.active:
                stage_text = None

        if game_started:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BG)

        if game_started and not game_over and not boss_active and not boss_spawning:
            score += dt*100

        if current_boss_index < len(boss_score_thresholds):
            if score >= boss_score_thresholds[current_boss_index] and not boss_active and not boss_spawning:
                boss_spawning = True
                for obs in obstacles[:]: 
                    if obs.obstacle.right < 0 or obs.obstacle.left > SCREEN_WIDTH:
                        obs.active = False
        
        if boss_spawning and not boss_active:
            all_obstacles_cleared = True
            for obs in obstacles:
                if obs.active:
                    if obs.obstacle.right > 0:
                        all_obstacles_cleared = False
                        break
            
            if all_obstacles_cleared:
                boss = Boss(boss_image_path, base.top)
                boss_active = True
                boss_spawning = False
                current_boss_index += 1

        player.handle_input(keys, dt, boss_fight=boss_active)
        player.apply_gravity(base, dt)

        if game_started:
            above.create(screen)
            above.move(dt)
            base.create(screen)
            base.move(dt)
        
        player.create(screen)

        if game_started and not boss_active and not boss_spawning:
            for obs in obstacles:
                if obs.active:
                    obs.move(dt)
                    if obs.obstacle.right > 0:
                        obs.create(screen)
                        if player.obstacle.colliderect(obs.hitbox()) and not game_over:
                            game_over = True
                            for ob in obstacles:
                                ob.active = False
                            base.active = False
                            player.collision = True
        elif boss_spawning:
            for obs in obstacles:
                if obs.active:
                    obs.move(dt)
                    if obs.obstacle.right > 0:
                        obs.create(screen)
                        if player.obstacle.colliderect(obs.hitbox()) and not game_over:
                            game_over = True
                            for ob in obstacles:
                                ob.active = False
                            base.active = False
                            player.collision = True

        if boss_active and boss is not None:
            boss.update(dt, player.obstacle)
            boss.create(screen, dt)
            boss.draw_health_bar(screen)
            
            if boss.active and not boss.appearing and not game_over:
                for laser in boss.lasers[:]:
                    if laser.age >= laser.lifetime or laser.age < 0:
                        continue
                    
                    player_rect = player.obstacle
                    x1, y1 = laser.start_pos
                    x2, y2 = laser.target_pos
                    half_width = laser.width / 2
                    
                    dx = x2 - x1
                    dy = y2 - y1
                    line_len_sq = dx*dx + dy*dy
                    
                    if line_len_sq < 0.0001:
                        expanded_rect = pygame.Rect(
                            player_rect.left - half_width,
                            player_rect.top - half_width,
                            player_rect.width + laser.width,
                            player_rect.height + laser.width
                        )
                        if expanded_rect.collidepoint(x1, y1):
                            if not game_over:
                                game_over = True
                        continue
                    
                    corners = [
                        (player_rect.left, player_rect.top),
                        (player_rect.right, player_rect.top),
                        (player_rect.right, player_rect.bottom),
                        (player_rect.left, player_rect.bottom),
                        (player_rect.centerx, player_rect.centery)
                    ]
                    
                    min_dist_sq = float('inf')
                    
                    for px, py in corners:
                        to_point_x = px - x1
                        to_point_y = py - y1
                        
                        t = (to_point_x * dx + to_point_y * dy) / line_len_sq
                        t = max(0, min(1, t)) 
                        
                        closest_x = x1 + t * dx
                        closest_y = y1 + t * dy
                        
                        dist_x = px - closest_x
                        dist_y = py - closest_y
                        dist_sq = dist_x * dist_x + dist_y * dist_y
                        min_dist_sq = min(min_dist_sq, dist_sq)
                    
                    intersects = False
                    if line_segment_intersect(x1, y1, x2, y2, 
                                             player_rect.left, player_rect.top, 
                                             player_rect.right, player_rect.top):
                        intersects = True
                    elif line_segment_intersect(x1, y1, x2, y2,
                                                 player_rect.right, player_rect.top,
                                                 player_rect.right, player_rect.bottom):
                        intersects = True
                    elif line_segment_intersect(x1, y1, x2, y2,
                                                 player_rect.right, player_rect.bottom,
                                                 player_rect.left, player_rect.bottom):
                        intersects = True
                    elif line_segment_intersect(x1, y1, x2, y2,
                                                 player_rect.left, player_rect.bottom,
                                                 player_rect.left, player_rect.top):
                        intersects = True
                    
                    if not intersects:
                        if (player_rect.left <= x1 <= player_rect.right and 
                            player_rect.top <= y1 <= player_rect.bottom):
                            intersects = True
                        elif (player_rect.left <= x2 <= player_rect.right and 
                              player_rect.top <= y2 <= player_rect.bottom):
                            intersects = True
                    
                    if intersects or min_dist_sq <= half_width * half_width:
                        if not game_over:
                            game_over = True
                
                for bullet in boss.bullets:
                    if player.obstacle.colliderect(bullet.rect):
                        if not game_over:
                            game_over = True
                        bullet.kill()
            

        shoot_timer -= dt
        
        if reloading:
            reload_time += dt
            if reload_time >= reload_duration:
                ammo = max_ammo
                reloading = False
                reload_time = 0
        
        if ammo == 0 and not reloading:
            reloading = True
            reload_time = 0
        
        if keys[pygame.K_f] and shoot_timer <= 0 and not game_over and not reloading:
            if ammo > 0:
                bullet_y = player.obstacle.centery
                bullet_x = player.obstacle.right
                bullets.add(Bullet(bullet_x, bullet_y))
                shoot_timer = shoot_cooldown
                ammo -= 1
                if ammo == 0:
                    reloading = True
                    reload_time = 0

        bullets.update(dt)
        bullets.draw(screen)

        if boss_active and boss is not None:
            for bullet in bullets:
                if boss.rect.colliderect(bullet.rect):
                    boss.hit(player, obstacles, base) 
                    bullet.kill()

        score_text = font.render(f"Score  : {str(int(score)).zfill(5)}", True, WHITE)
        screen.blit(score_text, (1050, 50))
        
        if reloading:
            ammo_text = font.render(f"Ammo : reloading.../{max_ammo}", True, (255, 200, 0))
        else:
            ammo_text = font.render(f"Ammo : {int(ammo)}/{max_ammo}", True, WHITE)
        screen.blit(ammo_text, (10, 50))
        if stage_text is not None:
            stage_text.draw(screen)

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            draw_center_text("Game Over", font, WHITE, SCREEN_HEIGHT//2 - 120)
            draw_center_text(f"Score: {int(score)}", font_small, MUTED, SCREEN_HEIGHT//2 - 60)

            btn_restart_draw(mouse_pos)
            btn_return_draw(mouse_pos)

    pygame.display.flip()

pygame.quit()
