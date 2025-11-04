import pygame
import random
import os
import math
import sys

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

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
icon_image = pygame.image.load(resource_path(os.path.join("Asset", "icon.JPG")))
player_image = "default.PNG"
player_jump_image = "jump.PNG"  
player_slide_image = "slide.PNG" 
roof_image_paths = [
    "roof1.PNG",
    "roof2.JPG",
    "roof3.JPG",
]
terrain_image = "terrain.JPG"
terrain_image_paths = [
    "terrain1.JPG",
    "terrain2.JPG",
    "terrain3.JPG",
]
boss_image_paths = [
    "boss1.PNG",  # Boss 1 image
    "boss2.PNG",  # Boss 2 image
    "boss3.PNG",  # Boss 3 image
]
background_image_paths = [
    "stage1.JPG",
    "stage2.JPG",
    "stage3.JPG", 
]
obstacle_images_paths = [
    "tall.PNG",
    "slidable.PNG",  # top-half hitbox
    "hanging.PNG", # hanging
    "huge.PNG", 
    "small.PNG"
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
num_obstacles = 999
obstacle_images = []
for path in obstacle_images_paths:
    image = pygame.image.load(resource_path(os.path.join("Asset", path))).convert_alpha()
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
slide_key_held = False 
ammo = 8 
max_ammo = 8
reloading = False
reload_time = 0
reload_duration = 2.0 
score = 0
boss_score_thresholds = [1000, 2300, 4200] #1000 2300 4200
current_boss_index = 0
boss_active = False
boss_spawning = False 
boss = None
stage_text = None
boss_point_rewards = [300, 500, 700] #300, 500, 700 

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

class BackgroundTransition:
    """Handles animated background transitions between stages"""
    def __init__(self):
        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 2.0  
        self.current_bg_x = 0
        self.next_bg_x = 0
        self.current_background_index = 0
        
    def start_transition(self, current_bg, next_bg):
        self.transitioning = True
        self.transition_timer = 0
        self.current_bg_image = current_bg
        self.next_bg_image = next_bg
        self.current_bg_x = 0
        self.next_bg_x = SCREEN_WIDTH  
        
    def update(self, dt):
        """Update transition animation"""
        if not self.transitioning:
            return
            
        self.transition_timer += dt
        progress = min(1.0, self.transition_timer / self.transition_duration)
        
        eased_progress = 1 - (1 - progress) ** 3
        
        self.current_bg_x = -eased_progress * SCREEN_WIDTH
        self.next_bg_x = SCREEN_WIDTH - eased_progress * SCREEN_WIDTH
        
        if progress >= 1.0:
            self.transitioning = False
            self.current_bg_x = 0
            self.next_bg_x = 0
    
    def draw(self, surface, default_bg):
        """Draw the background with transition effect"""
        bg_y = 125
        if self.transitioning:
            surface.blit(self.current_bg_image, (self.current_bg_x, bg_y))
            surface.blit(self.next_bg_image, (self.next_bg_x, bg_y))
            if self.current_bg_x < 0:
                surface.blit(self.next_bg_image, (self.current_bg_x + SCREEN_WIDTH, bg_y))
            if self.next_bg_x > 0:
                surface.blit(self.current_bg_image, (self.next_bg_x - SCREEN_WIDTH, bg_y))
        else:
            surface.blit(default_bg, (0, bg_y))

class Player:
    def __init__(self, image_path, x, y, jump_image_path=None, slide_image_path=None):
        self.original_image = pygame.image.load(resource_path(os.path.join("Asset", image_path))).convert_alpha()
        self.normal_width = 100
        self.jumping_width = 130
        self.image_normal = pygame.transform.scale(self.original_image, (self.normal_width, 200))
        
        if jump_image_path:
            jump_img = pygame.image.load(resource_path(os.path.join("Asset", jump_image_path))).convert_alpha()
            self.jumping_height = 180
            self.image_jump = pygame.transform.scale(jump_img, (self.jumping_width, self.jumping_height))
        else:
            self.jumping_height = 180
            self.image_jump = pygame.transform.scale(self.original_image, (self.jumping_width, self.jumping_height))
        
        if slide_image_path:
            slide_img = pygame.image.load(resource_path(os.path.join("Asset", slide_image_path))).convert_alpha()
            self.sliding_height = 80
            self.image_slide = pygame.transform.scale(slide_img, (175, self.sliding_height))
        else:
            self.sliding_height = 80
            self.image_slide = pygame.transform.scale(self.original_image, (175, self.sliding_height))
        self.start_x = x
        self.obstacle = self.image_normal.get_rect(midbottom=(x, y))
        self.normal_height = 200
        self.velocity = 0
        self.gravity = 2500
        self.jump_strength = -1125
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False
        self.move_speed = 400

    def handle_input(self, keys, dt, boss_fight=False):
        global game_started, slide_key_held, boss
        if not game_over:
            if boss_fight:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.obstacle.x -= self.move_speed * dt
                    self.obstacle.x = max(0, self.obstacle.x)
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.obstacle.x += self.move_speed * dt
                    if boss is not None and boss.active:
                        max_x = boss.rect.left - self.obstacle.width - 10  
                        self.obstacle.x = min(max_x, self.obstacle.x)
                    else:
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
        self.obstacle.midbottom = (self.start_x, base.top)
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
    def __init__(self, texture, x, y):
        self.texture = texture
        self.roof = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.speed = 600
        self.active = True
        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 2.0
        self.current_texture = texture
        self.next_texture = None
        self.current_x = 0
        self.next_x = 0

    def start_transition(self, current_texture, next_texture):
        self.transitioning = True
        self.transition_timer = 0
        self.current_texture = current_texture
        self.next_texture = next_texture
        self.current_x = 0
        self.next_x = SCREEN_WIDTH

    def update_transition(self, dt):
        if not self.transitioning:
            return
        
        self.transition_timer += dt
        progress = min(1.0, self.transition_timer / self.transition_duration)
        eased_progress = 1 - (1 - progress) ** 3
        
        self.current_x = -eased_progress * SCREEN_WIDTH
        self.next_x = SCREEN_WIDTH - eased_progress * SCREEN_WIDTH
        
        if progress >= 1.0:
            self.transitioning = False
            self.texture = self.next_texture
            self.current_texture = self.next_texture
            self.current_x = 0
            self.next_x = 0

    def set_texture(self, texture):
        self.texture = texture
        self.current_texture = texture

    def move(self, dt):
        if not game_over and self.active and game_started:
            for i in range(2):
                self.roof[i].x -= self.speed * dt
            if self.roof[0].right <= 0:
                self.roof[0].x = self.roof[1].right
            if self.roof[1].right <= 0:
                self.roof[1].x = self.roof[0].right

    def create(self, surface):
        if self.transitioning:
            for i in range(2):
                base_x = self.roof[i].x
                base_y = self.roof[i].y
                
                current_x = base_x + self.current_x
                next_x = base_x + self.next_x
                
                surface.blit(self.current_texture, (current_x, base_y))
                surface.blit(self.next_texture, (next_x, base_y))
                
                if current_x < 0:
                    surface.blit(self.next_texture, (current_x + SCREEN_WIDTH, base_y))
                if next_x > SCREEN_WIDTH:
                    surface.blit(self.current_texture, (next_x - SCREEN_WIDTH, base_y))
                
                surface.blit(self.current_texture, (current_x + SCREEN_WIDTH, base_y))
                surface.blit(self.next_texture, (next_x + SCREEN_WIDTH, base_y))
        else:
            for i in self.roof:
                surface.blit(self.texture, i)

    @property
    def bottom(self):
        return self.roof[0].bottom

class Terrain:
    def __init__(self, texture, x, y):
        self.texture = texture
        self.terrain = [
            self.texture.get_rect(topleft=(x, y)),
            self.texture.get_rect(topleft=(x + SCREEN_WIDTH, y))
        ]
        self.active = True
        self.speed = 600
        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 2.0
        self.current_texture = texture
        self.next_texture = None
        self.current_x = 0
        self.next_x = 0

    def start_transition(self, current_texture, next_texture):
        self.transitioning = True
        self.transition_timer = 0
        self.current_texture = current_texture
        self.next_texture = next_texture
        self.current_x = 0
        self.next_x = SCREEN_WIDTH

    def update_transition(self, dt):
        if not self.transitioning:
            return
        
        self.transition_timer += dt
        progress = min(1.0, self.transition_timer / self.transition_duration)
        eased_progress = 1 - (1 - progress) ** 3
        
        self.current_x = -eased_progress * SCREEN_WIDTH
        self.next_x = SCREEN_WIDTH - eased_progress * SCREEN_WIDTH
        
        if progress >= 1.0:
            self.transitioning = False
            self.texture = self.next_texture
            self.current_texture = self.next_texture
            self.current_x = 0
            self.next_x = 0

    def set_texture(self, texture):
        self.texture = texture
        self.current_texture = texture

    def move(self, dt):
        if not game_over and self.active and game_started:
            for i in range(2):
                self.terrain[i].x -= self.speed * dt
            if self.terrain[0].right <= 0:
                self.terrain[0].x = self.terrain[1].right
            if self.terrain[1].right <= 0:
                self.terrain[1].x = self.terrain[0].right

    def create(self, surface):
        if self.transitioning:
            for i in range(2):
                base_x = self.terrain[i].x
                base_y = self.terrain[i].y
                
                current_x = base_x + self.current_x
                next_x = base_x + self.next_x
                
                surface.blit(self.current_texture, (current_x, base_y))
                surface.blit(self.next_texture, (next_x, base_y))
                
                if current_x < 0:
                    surface.blit(self.next_texture, (current_x + SCREEN_WIDTH, base_y))
                if next_x > SCREEN_WIDTH:
                    surface.blit(self.current_texture, (next_x - SCREEN_WIDTH, base_y))
                
                surface.blit(self.current_texture, (current_x + SCREEN_WIDTH, base_y))
                surface.blit(self.next_texture, (next_x + SCREEN_WIDTH, base_y))
        else:
            for i in self.terrain:
                surface.blit(self.texture, i)

    @property
    def top(self):
        return self.terrain[0].top

class TopBottomLaserWarning:
    """Warning for top/bottom laser beam"""
    def __init__(self, x, from_top):
        self.x = x
        self.width = 30
        self.height = SCREEN_HEIGHT
        self.age = 0
        self.warning_duration = 1.0
        
    def update(self, dt):
        self.age += dt
        
    def draw(self, surface):
        if self.age < self.warning_duration:
            pulse_time = pygame.time.get_ticks() * 0.003
            alpha = int(70 + 50 * (0.5 + 0.5 * math.sin(pulse_time)))
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (255, 0, 0, alpha), (0, 0, self.width, self.height))
            surface.blit(temp_surface, (self.x - self.width // 2, 0))
    
    def is_complete(self):
        return self.age >= self.warning_duration

class TopBottomLaser:
    """Laser beam that shoots from top or bottom"""
    def __init__(self, x, from_top):
        self.x = x
        self.width = 30
        self.height = SCREEN_HEIGHT
        self.active = True
        self.lifetime = 1.5  
        self.age = 0
        
    def update(self, dt):
        if not self.active:
            return
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
    
    def draw(self, surface):
        if self.active:
            alpha = int(220 + 35 * math.sin(pygame.time.get_ticks() * 0.02))
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (255, 50, 50, alpha), (0, 0, self.width, self.height))
            center_line_width = max(2, self.width // 5)
            center_x = (self.width - center_line_width) // 2
            pygame.draw.rect(temp_surface, (255, 0, 0, min(255, alpha + 50)), 
                           (center_x, 0, center_line_width, self.height))
            surface.blit(temp_surface, (self.x - self.width // 2, 0))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.width // 2, 0, self.width, self.height)

class LaserWarning:
    """Preview/shadow showing where a laser will appear"""
    def __init__(self, start_x, start_y, target_x, target_y):
        self.start_pos = (start_x, start_y)
        self.target_pos = (target_x, target_y)
        self.width = 8 
        self.age = 0
        self.warning_duration = 0.8
        
    def update(self, dt):
        self.age += dt
        
    def draw(self, surface):
        if self.age < self.warning_duration:
            alpha = int(80 + 100 * (0.5 + 0.5 * math.sin(self.age * 12)))
            color = (255, 0, 0) 
            
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            pygame.draw.line(temp_surface, (*color, alpha), self.start_pos, self.target_pos, self.width)
            
            surface.blit(temp_surface, (0, 0))
            
    def is_complete(self):
        return self.age >= self.warning_duration

class BossLaser(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__()
        self.start_pos = (start_x, start_y)
        self.target_pos = (target_x, target_y)
        self.width = 15
        self.color = (255, 255, 150)  
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
        self.image = pygame.Surface((20, 8))
        self.image.fill((255, 100, 100))
        speed = (velocity_x**2 + velocity_y**2)**0.5
        if speed > 0:
            angle = math.atan2(velocity_y, velocity_x)
            self.image = pygame.transform.rotate(self.image, -math.degrees(angle))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        
    def update(self, dt):
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class HorizontalLaserWarning:
    """Warning preview for horizontal moving laser"""
    def __init__(self, y, hole_start_x, hole_end_x):
        self.y = y
        self.hole_start_x = hole_start_x
        self.hole_end_x = hole_end_x
        self.width = 25
        self.age = 0
        self.warning_duration = 1.0
        
    def update(self, dt):
        self.age += dt
        
    def draw(self, surface):
        if self.age < self.warning_duration:
            pulse_time = pygame.time.get_ticks() * 0.003 
            alpha = int(70 + 50 * (0.5 + 0.5 * math.sin(pulse_time)))
            temp_surface = pygame.Surface((SCREEN_WIDTH, self.width), pygame.SRCALPHA)
            
            if self.hole_start_x > 0:
                pygame.draw.rect(temp_surface, (255, 0, 0, alpha), (0, 0, self.hole_start_x, self.width))
            if self.hole_end_x < SCREEN_WIDTH:
                pygame.draw.rect(temp_surface, (255, 0, 0, alpha), (self.hole_end_x, 0, SCREEN_WIDTH - self.hole_end_x, self.width))
            
            surface.blit(temp_surface, (0, self.y - self.width // 2))
    
    def is_complete(self):
        return self.age >= self.warning_duration

class HorizontalLaser:
    """Horizontal laser that moves vertically with a hole for player to escape"""
    def __init__(self, y, target_y, hole_start_x, hole_end_x, move_down=True):
        self.y = y
        self.target_y = target_y
        self.hole_start_x = hole_start_x
        self.hole_end_x = hole_end_x
        self.width = 25
        self.active = True
        self.speed = 350
        self.move_down = move_down  
        self.disappear_distance = 50
        
    def update(self, dt):
        if not self.active:
            return
        
        if self.move_down:
            if self.y < self.target_y:
                self.y += self.speed * dt
                if self.y >= self.target_y - self.disappear_distance:
                    self.active = False
            else:
                self.active = False
        else:
            if self.y > self.target_y:
                self.y -= self.speed * dt
                if self.y <= self.target_y + self.disappear_distance:
                    self.active = False
            else:
                self.active = False
    
    def draw(self, surface):
        if self.active:
            temp_surface = pygame.Surface((SCREEN_WIDTH, self.width), pygame.SRCALPHA)
            alpha = int(220 + 35 * math.sin(pygame.time.get_ticks() * 0.02))
            
            if self.hole_start_x > 0:
                pygame.draw.rect(temp_surface, (255, 50, 50, alpha), (0, 0, self.hole_start_x, self.width))
            if self.hole_end_x < SCREEN_WIDTH:
                pygame.draw.rect(temp_surface, (255, 50, 50, alpha), (self.hole_end_x, 0, SCREEN_WIDTH - self.hole_end_x, self.width))
            
            surface.blit(temp_surface, (0, self.y - self.width // 2))
    
    def get_rects(self):
        """Get collision rectangles (two segments for the hole)"""
        rects = []
        if self.hole_start_x > 0:
            rects.append(pygame.Rect(0, self.y - self.width // 2, self.hole_start_x, self.width))
        if self.hole_end_x < SCREEN_WIDTH:
            rects.append(pygame.Rect(self.hole_end_x, self.y - self.width // 2, SCREEN_WIDTH - self.hole_end_x, self.width))
        return rects

class VerticalLaser:
    """Vertical laser that moves horizontally towards player's default position"""
    def __init__(self, x, target_x, terrain_top):
        self.x = x
        self.target_x = target_x  # Player's default position (around x=100)
        self.width = 30  # Made wider for better visibility
        self.height = SCREEN_HEIGHT
        self.active = True
        self.speed = 400  # Faster movement speed for better visibility
        self.disappear_distance = 50  # Disappear when within 50 pixels of target
        
    def update(self, dt):
        if not self.active:
            return
            
        if self.x < self.target_x:
            self.x += self.speed * dt
            if self.x >= self.target_x - self.disappear_distance:
                self.active = False
        elif self.x > self.target_x:
            self.x -= self.speed * dt
            if self.x <= self.target_x + self.disappear_distance:
                self.active = False
        else:
            self.active = False
    
    def draw(self, surface):
        if self.active:
            alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.015))
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (255, 50, 50, alpha), (0, 0, self.width, self.height))
            center_line_width = max(2, self.width // 5)
            center_x = (self.width - center_line_width) // 2
            pygame.draw.rect(temp_surface, (255, 0, 0, min(255, alpha + 50)), 
                           (center_x, 0, center_line_width, self.height))
            surface.blit(temp_surface, (self.x - self.width // 2, 0))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.width // 2, 0, self.width, self.height)

class Boss:
    def __init__(self, image_path, terrain_top, boss_index=0):
        self.original_image = pygame.image.load(resource_path(os.path.join("Asset", image_path))).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (200, 300))
        self.rect = self.image.get_rect(bottomright=(SCREEN_WIDTH - 30, terrain_top))
        boss_hp_values = [668, 927, 1339]
        if boss_index < len(boss_hp_values):
            self.max_hp = boss_hp_values[boss_index]
        else:
            self.max_hp = boss_hp_values[-1]
        self.hp = self.max_hp
        self.boss_index = boss_index
        self.active = True
        self.attack_timer = 0
        self.attack_cooldown = 2.0
        self.lasers = []
        self.laser_warnings = [] 
        self.bullets = pygame.sprite.Group()
        self.vertical_lasers = []  # For vertical moving lasers (boss 2)
        self.horizontal_lasers = []  # For horizontal moving lasers with holes (boss 2)
        self.horizontal_laser_warnings = []  # Warnings for horizontal lasers
        self.horizontal_laser_barrage_active = False
        self.horizontal_laser_barrage_timer = 0
        self.horizontal_laser_barrage_delay = 2.5  # Time between each warning/laser (increased for player reaction)
        self.horizontal_laser_warning_timer = 0
        self.horizontal_laser_warning_delay = 1.4  # Time warning shows before laser fires (increased)
        self.current_warning_index = 0  # Which warning is currently showing
        self.horizontal_laser_data = []  # Store laser data for barrage
        self.top_bottom_lasers = []  # For top/bottom laser beams (boss 3)
        self.top_bottom_laser_warnings = []  # Warnings for top/bottom lasers
        self.top_bottom_laser_count = 0  # Number of lasers in current attack (10 total)
        self.top_bottom_laser_active = False
        self.top_bottom_laser_timer = 0
        self.top_bottom_laser_delay = 1.5  # Time between each top/bottom laser
        self.top_bottom_laser_warning_timer = 0
        self.top_bottom_laser_warning_delay = 1.0  # Warning duration before laser fires
        self.head_laser_warnings = []  # For head laser barrage (boss 3)
        self.head_laser_data = []  # Data for head laser barrage
        self.smg_burst_count = 0 
        self.smg_burst_delay = 0.1
        self.smg_timer = 0
        self.animation_timer = 0
        self.appearing = True
        self.appear_duration = 1.5
        self.start_x = SCREEN_WIDTH + 300
        self.target_x = SCREEN_WIDTH - 30
        self.current_x = self.start_x
        self.grace_period = 0.5
        self.grace_timer = 0
        self.warning_timer = 0
        self.warning_duration = 0.8 
        self.pending_attack = None 
        self.pending_laser_data = []
        self.defeated = False
        self.defeat_duration = 1.5
        self.defeat_timer = 0 

    def update(self, dt, player_rect):
        if not self.active:
            return
        
        if self.defeated:
            self.defeat_timer += dt
            if self.defeat_timer < self.defeat_duration:
                progress = self.defeat_timer / self.defeat_duration
                exit_x = SCREEN_WIDTH + 300
                self.current_x = self.target_x + (exit_x - self.target_x) * progress
                self.rect.right = self.current_x
            else:
                self.active = False
                self.defeated = False
                global background_transition, background_stages, current_background_index, background_image, current_boss_index, roof_stages, terrain_stages, above, base
                if not background_transition.transitioning:
                    next_bg_index = min(self.boss_index + 1, 2)
                    if current_background_index != next_bg_index:
                        current_bg = background_stages[current_background_index] if current_background_index < len(background_stages) else background_stages[0]
                        next_bg = background_stages[next_bg_index]
                        background_transition.start_transition(current_bg, next_bg)
                        background_image = next_bg
                        current_roof = roof_stages[current_background_index] if current_background_index < len(roof_stages) else roof_stages[0]
                        next_roof = roof_stages[next_bg_index]
                        above.start_transition(current_roof, next_roof)
                        current_terrain = terrain_stages[current_background_index] if current_background_index < len(terrain_stages) else terrain_stages[0]
                        next_terrain = terrain_stages[next_bg_index]
                        base.start_transition(current_terrain, next_terrain)
                        current_background_index = next_bg_index
            return
            
        if self.appearing:
            self.animation_timer += dt
            if self.animation_timer < self.appear_duration:
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
                if self.horizontal_laser_barrage_active or self.top_bottom_laser_active:
                    pass
                else:
                    if self.smg_burst_count > 0:
                        self.smg_timer += dt
                        if self.smg_timer >= self.smg_burst_delay:
                            self.smg_timer = 0
                            self.smg_burst_count -= 1
                            self.fire_smg_bullet(player_rect)
                    elif self.pending_attack is not None:
                        if self.pending_attack == "barrage":
                            self.warning_timer += dt
                            for warning in self.laser_warnings:
                                warning.age += dt
                            if self.warning_timer >= self.warning_duration:
                                self._execute_attack(player_rect)
                                self.pending_attack = None
                                self.warning_timer = 0
                                self.pending_laser_data = []
                        elif self.pending_attack == "horizontal_laser_barrage":
                            self._execute_attack(player_rect)
                            self.pending_attack = None
                            self.warning_timer = 0
                        elif self.pending_attack == "head_laser_barrage" or self.pending_attack == "direct_laser":
                            self.warning_timer += dt
                            for warning in self.head_laser_warnings:
                                warning.age += dt
                            if self.warning_timer >= self.warning_duration:
                                self._execute_attack(player_rect)
                                self.pending_attack = None
                                self.warning_timer = 0
                        elif self.pending_attack == "top_bottom_laser":
                            self._execute_attack(player_rect)
                            self.pending_attack = None
                            self.warning_timer = 0
                        else:
                            self.warning_timer += dt
                            if self.warning_timer >= 0.3:
                                self._execute_attack(player_rect)
                                self.pending_attack = None
                                self.warning_timer = 0
                                self.pending_laser_data = []
                    else:
                        if not self.horizontal_laser_barrage_active and not self.top_bottom_laser_active:
                            self.attack_timer += dt
                            if self.attack_timer >= self.attack_cooldown:
                                self.attack_timer = 0
                                self._start_attack(player_rect)
        
        self.bullets.update(dt)
        
        for v_laser in self.vertical_lasers[:]:
            v_laser.update(dt)
            if not v_laser.active:
                self.vertical_lasers.remove(v_laser)
        
        for warning in self.horizontal_laser_warnings[:]:
            warning.update(dt)
            if warning.is_complete():
                self.horizontal_laser_warnings.remove(warning)
        
        for h_laser in self.horizontal_lasers[:]:
            h_laser.update(dt)
            if not h_laser.active:
                self.horizontal_lasers.remove(h_laser)
        
        if self.horizontal_laser_barrage_active:
            self.horizontal_laser_barrage_timer += dt
            
            for warning in self.horizontal_laser_warnings:
                warning.update(dt)
            
            if len(self.horizontal_laser_warnings) > 0:
                self.horizontal_laser_warning_timer += dt
                
                if self.horizontal_laser_warning_timer >= self.horizontal_laser_warning_delay:
                    if self.current_warning_index < len(self.horizontal_laser_data):
                        laser_data = self.horizontal_laser_data[self.current_warning_index]
                        start_y = -50
                        target_y = SCREEN_HEIGHT + 50
                        h_laser = HorizontalLaser(
                            start_y, 
                            target_y, 
                            laser_data['hole_start'], 
                            laser_data['hole_end'],
                            move_down=True
                        )
                        self.horizontal_lasers.append(h_laser)
                        self.horizontal_laser_warnings.clear()
                        self.current_warning_index += 1
                        self.horizontal_laser_warning_timer = 0
                        self.horizontal_laser_barrage_timer = 0  # Reset for gap timing
            else:
                if self.horizontal_laser_barrage_timer >= (self.horizontal_laser_barrage_delay - self.horizontal_laser_warning_delay):
                    if self.current_warning_index < len(self.horizontal_laser_data):
                        self._show_next_warning()
                        self.horizontal_laser_barrage_timer = 0
                    else:
                        self.horizontal_laser_barrage_active = False
                        self.current_warning_index = 0
                        self.horizontal_laser_warning_timer = 0
        
        if self.top_bottom_laser_active:
            self.top_bottom_laser_timer += dt
            
            for warning in self.top_bottom_laser_warnings:
                warning.update(dt)
            
            if len(self.top_bottom_laser_warnings) > 0:
                self.top_bottom_laser_warning_timer += dt
                
                if self.top_bottom_laser_warning_timer >= self.top_bottom_laser_warning_delay:
                    warning = self.top_bottom_laser_warnings[0]
                    laser = TopBottomLaser(warning.x, warning.from_top)
                    self.top_bottom_lasers.append(laser)
                    self.top_bottom_laser_warnings.clear()
                    self.top_bottom_laser_count -= 1
                    self.top_bottom_laser_warning_timer = 0
                    self.top_bottom_laser_timer = 0
                    
                    if self.top_bottom_laser_count > 0:
                        self._fire_next_top_bottom_laser()
                    else:
                        self.top_bottom_laser_active = False
            else:
                if self.top_bottom_laser_timer >= (self.top_bottom_laser_delay - self.top_bottom_laser_warning_delay):
                    if self.top_bottom_laser_count > 0:
                        self._fire_next_top_bottom_laser()
                        self.top_bottom_laser_timer = 0
                    else:
                        self.top_bottom_laser_active = False
        
        for t_laser in self.top_bottom_lasers[:]:
            t_laser.update(dt)
            if not t_laser.active:
                self.top_bottom_lasers.remove(t_laser)
        
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
        if self.horizontal_laser_barrage_active:
            return
            
        if self.boss_index == 1:
            attack_type = random.choices(
                ["smg", "horizontal_laser_barrage", "vertical_laser"],
                weights=[4, 2, 4],  
                k=1
            )[0]
        elif self.boss_index == 2:
            if self.top_bottom_laser_active or self.horizontal_laser_barrage_active:
                return
            else:
                attack_type = random.choices(
                    ["smg", "barrage", "head_laser_barrage", "direct_laser", "horizontal_laser_barrage", "vertical_laser", "top_bottom_laser"],
                    weights=[2, 2, 2, 2, 2, 2, 2], 
                    k=1
                )[0]
        else:
            attack_type = random.choice(["smg", "barrage"])
        
        self.pending_attack = attack_type
        
        if attack_type == "barrage":
            self._create_laser_warnings(player_rect)
        elif attack_type == "horizontal_laser_barrage":
            self._create_horizontal_laser_warnings()
        elif attack_type == "head_laser_barrage":
            self._create_head_laser_warnings(player_rect)
        elif attack_type == "direct_laser":
            self._create_direct_laser_warning(player_rect)
        elif attack_type == "top_bottom_laser":
            self._start_top_bottom_laser()
        elif attack_type == "vertical_laser":
            pass
    
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
                
                start_x = self.rect.centerx
                start_y = self.rect.top + 50
                
                self.pending_laser_data.append({
                    'start': (start_x, start_y),
                    'target': (target_x, target_y)
                })
                
                warning = LaserWarning(start_x, start_y, target_x, target_y)
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
        elif self.pending_attack == "horizontal_laser_barrage":
            self.horizontal_laser_barrage_active = True
            self.horizontal_laser_barrage_timer = 0
            self.horizontal_laser_warning_timer = 0
            self.current_warning_index = 0
        elif self.pending_attack == "head_laser_barrage":
            for laser_data in self.head_laser_data:
                laser = BossLaser(laser_data['start'][0], laser_data['start'][1], 
                                 laser_data['target'][0], laser_data['target'][1])
                self.lasers.append(laser)
            self.head_laser_warnings.clear()
            self.head_laser_data = []
        elif self.pending_attack == "direct_laser":
            for laser_data in self.head_laser_data:
                laser = BossLaser(laser_data['start'][0], laser_data['start'][1], 
                                 laser_data['target'][0], laser_data['target'][1])
                self.lasers.append(laser)
            self.head_laser_warnings.clear()
            self.head_laser_data = []
        elif self.pending_attack == "top_bottom_laser":
            pass
        elif self.pending_attack == "vertical_laser":
            self._fire_vertical_laser(player_rect)
    
    def _create_horizontal_laser_warnings(self):
        """Create laser data for horizontal laser barrage - warnings shown one at a time"""
        barrage_count = 5
        
        y_pos = SCREEN_HEIGHT // 2
        
        boss_x_min = SCREEN_WIDTH - 30 - 150  # Boss target position - buffer (boss is on right side)
        boss_x_max = SCREEN_WIDTH - 30 + 50   # Boss target position + buffer
        
        self.horizontal_laser_data = []
        self.horizontal_laser_warnings.clear()
        
        for _ in range(barrage_count):
            hole_size = 200  # Fixed hole size - consistent and slightly bigger
            
            max_attempts = 20
            hole_start = None
            
            for _ in range(max_attempts):
                candidate_start = random.randint(50, SCREEN_WIDTH - hole_size - 50)
                candidate_end = candidate_start + hole_size
                
                hole_overlaps_boss = not (candidate_end < boss_x_min or candidate_start > boss_x_max)
                
                if not hole_overlaps_boss:
                    hole_start = candidate_start
                    break
            
            if hole_start is None:
                hole_start = random.randint(50, boss_x_min - hole_size - 20)
            
            hole_end = hole_start + hole_size
            
            self.horizontal_laser_data.append({
                'y': y_pos,
                'hole_start': hole_start,
                'hole_end': hole_end
            })
        
        self.current_warning_index = 0
        self.horizontal_laser_warning_timer = 0
        self._show_next_warning()
    
    def _show_next_warning(self):
        """Show the next warning in sequence"""
        if self.current_warning_index < len(self.horizontal_laser_data):
            laser_data = self.horizontal_laser_data[self.current_warning_index]
            warning = HorizontalLaserWarning(laser_data['y'], laser_data['hole_start'], laser_data['hole_end'])
            self.horizontal_laser_warnings.clear()  # Only show one warning at a time
            self.horizontal_laser_warnings.append(warning)
    
    def _create_head_laser_warnings(self, player_rect):
        """Create warnings for head laser barrage (from boss head, NOT directed at player - random spread)"""
        barrage_count = 5
        
        self.head_laser_data = []
        self.head_laser_warnings.clear()
        
        laser_start_x = self.rect.centerx
        laser_start_y = self.rect.top + 50
        
        for _ in range(barrage_count):
            dir_x = player_rect.centerx - laser_start_x
            dir_y = player_rect.centery - laser_start_y
            base_angle = math.atan2(dir_y, dir_x)
            spread_range = random.uniform(-0.8, 0.8)  # Wider spread
            angle = base_angle + spread_range
            
            target_dist = random.uniform(1500, 2500)
            
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            
            target_x = laser_start_x + dir_x * target_dist
            target_y = laser_start_y + dir_y * target_dist
            
            self.head_laser_data.append({
                'start': (laser_start_x, laser_start_y),
                'target': (target_x, target_y)
            })
            
            warning = LaserWarning(laser_start_x, laser_start_y, target_x, target_y)
            self.head_laser_warnings.append(warning)
    
    def _create_direct_laser_warning(self, player_rect):
        """Create a single laser from boss head directly at player"""
        self.head_laser_data = []
        self.head_laser_warnings.clear()
        
        laser_start_x = self.rect.centerx
        laser_start_y = self.rect.top + 50  # From boss head
        
        dir_x = player_rect.centerx - laser_start_x
        dir_y = player_rect.centery - laser_start_y
        dist = (dir_x**2 + dir_y**2)**0.5
        if dist > 0:
            dir_x /= dist
            dir_y /= dist
            
            target_dist = 2000
            target_x = laser_start_x + dir_x * target_dist
            target_y = laser_start_y + dir_y * target_dist
            
            self.head_laser_data.append({
                'start': (laser_start_x, laser_start_y),
                'target': (target_x, target_y)
            })
            
            warning = LaserWarning(laser_start_x, laser_start_y, target_x, target_y)
            self.head_laser_warnings.append(warning)
    
    def _start_top_bottom_laser(self):
        """Start the top/bottom laser beam attack sequence"""
        self.top_bottom_laser_count = 10  
        self.top_bottom_laser_active = True
        self.top_bottom_laser_timer = 0
        self.top_bottom_laser_warning_timer = 0
        self._fire_next_top_bottom_laser()
    
    def _fire_next_top_bottom_laser(self):
        """Fire the next top/bottom laser with warning"""
        from_top = random.choice([True, False])
        x_pos = random.randint(100, SCREEN_WIDTH - 100)
        
        warning = TopBottomLaserWarning(x_pos, from_top)
        self.top_bottom_laser_warnings.clear()  
        self.top_bottom_laser_warnings.append(warning)
        self.top_bottom_laser_warning_timer = 0
    
    def _fire_vertical_laser(self, player_rect):
        start_x = SCREEN_WIDTH + 50
        target_x = 100  
        v_laser = VerticalLaser(start_x, target_x, self.rect.bottom)
        self.vertical_lasers.append(v_laser)
    
    def create(self, surface, dt):
        if self.active or self.defeated:
            surface.blit(self.image, self.rect)
            for warning in self.laser_warnings[:]:
                warning.draw(surface)
                if warning.is_complete():
                    self.laser_warnings.remove(warning)
            for warning in self.horizontal_laser_warnings:
                warning.draw(surface)
            for warning in self.head_laser_warnings:
                warning.draw(surface)
            for warning in self.top_bottom_laser_warnings:
                warning.draw(surface)
            for laser in self.lasers[:]:
                laser.draw(surface)
                laser.update(dt)
                if laser.age >= laser.lifetime:
                    self.lasers.remove(laser)
            self.bullets.draw(surface)
            for v_laser in self.vertical_lasers:
                v_laser.draw(surface)
            for h_laser in self.horizontal_lasers:
                h_laser.draw(surface)
            for t_laser in self.top_bottom_lasers:
                t_laser.draw(surface)

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
        self.hp -= 26
        if self.hp <= 0:
            self.defeated = True
            self.defeat_timer = 0
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
                player_ref.obstacle.midbottom = (100, base_ref.top)
                player_ref.obstacle.width = player_ref.normal_width
                player_ref.obstacle.height = player_ref.normal_height
                player_ref.velocity = 0
                player_ref.on_ground = True
                player_ref.falling = False
                player_ref.collision = False
                player_ref.sliding = False
            
            if obstacles_ref is not None and base_ref is not None:
                x = SCREEN_WIDTH + 100
                initial_obstacle_count = 5
                for i, obs in enumerate(obstacles_ref):
                    if i < initial_obstacle_count:
                        obs.active = True
                        obs.type = random.randint(0, 4)
                        obs.hanging = obs.type == 2
                        obs.top_half_hitbox = obs.type == 1
                        obs.reset(x, base_ref.top)
                        x += random.randint(550, 700)
                    else:
                        obs.active = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        paper_width = 60
        paper_height = 40
        self.image = pygame.Surface((paper_width, paper_height), pygame.SRCALPHA)
        self.image.fill((255, 255, 250))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, paper_width, paper_height), 2)
        resign_font = pygame.font.Font(None, 18)
        resign_text = resign_font.render("RESIGN", True, (0, 0, 0))
        text_rect = resign_text.get_rect(center=(paper_width // 2, paper_height // 2))
        self.image.blit(resign_text, text_rect)
        self.rect = self.image.get_rect(midleft=(x, y))
        self.speed = 1000

    def update(self, dt):
        self.rect.x += self.speed * dt
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

# ------------------------- Game Objects -------------------------
background_stages = []
for i, path in enumerate(background_image_paths):
    try:
        bg = pygame.image.load(resource_path(os.path.join("Asset", path))).convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, 525))
        
        background_stages.append(bg)
    except:
        base_bg = pygame.image.load(resource_path(os.path.join("Asset", background_image_paths[0]))).convert()
        base_bg = pygame.transform.scale(base_bg, (SCREEN_WIDTH, 525))
        background_stages.append(base_bg)

roof_stages = []
for i, path in enumerate(roof_image_paths):
    try:
        roof_img = pygame.image.load(resource_path(os.path.join("Asset", path))).convert_alpha()
        roof_texture = pygame.transform.scale(roof_img, (SCREEN_WIDTH, 125))
        roof_stages.append(roof_texture)
    except:
        base_roof = pygame.image.load(resource_path(os.path.join("Asset", roof_image_paths[0]))).convert_alpha()
        base_roof_texture = pygame.transform.scale(base_roof, (SCREEN_WIDTH, 125))
        roof_stages.append(base_roof_texture)

terrain_stages = []
for i, path in enumerate(terrain_image_paths):
    try:
        terrain_img = pygame.image.load(resource_path(os.path.join("Asset", path))).convert_alpha()
        terrain_texture = pygame.transform.scale(terrain_img, (SCREEN_WIDTH, 150))
        terrain_stages.append(terrain_texture)
    except:
        base_terrain = pygame.image.load(resource_path(os.path.join("Asset", terrain_image_paths[0]))).convert_alpha()
        base_terrain_texture = pygame.transform.scale(base_terrain, (SCREEN_WIDTH, 150))
        terrain_stages.append(base_terrain_texture)

current_background_index = 0
background_image = background_stages[0]  # Default to first stage
background_transition = BackgroundTransition()

bullets = pygame.sprite.Group()
shoot_cooldown = 0.3
shoot_timer = 0

above = Roof(roof_stages[0], 0, 0)
base = Terrain(terrain_stages[0], 0, 650)
player = Player(player_image, 100, base.top, player_jump_image, player_slide_image)

obstacles = []
x = 1100
for _ in range(num_obstacles):
    obstacles.append(Obstacle(x, base.top))
    x += random.randint(550, 700)

def spawn_obstacle(obs):
    global boss_spawning, boss_active, boss
    if boss_spawning or boss_active or (boss is not None and boss.defeated):
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
    global game_over, game_started, prev_game_started, score, current_boss_index, boss_active, boss, stage_text, ammo, boss_spawning, reloading, reload_time, current_background_index, background_image, background_transition, roof_stages, terrain_stages, above, base
    player.reset()
    current_background_index = 0
    background_image = background_stages[0]
    background_transition.transitioning = False
    background_transition.transition_timer = 0
    above.set_texture(roof_stages[0])
    above.transitioning = False
    above.transition_timer = 0
    base.set_texture(terrain_stages[0])
    base.transitioning = False
    base.transition_timer = 0
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
            if state == START_PROMPT:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                    state = GAME
                    game_started = True
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        if player.on_ground and not player.sliding:
                            player.velocity = player.jump_strength
                            player.on_ground = False
            elif state == GAME and not game_over:
                is_jump_key = (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP)
                
                if is_jump_key:
                    if not boss_active:
                        near_ground = abs(player.obstacle.bottom - base.top) < 20
                        if player.on_ground or near_ground:
                            if not player.sliding or near_ground:
                                player.velocity = player.jump_strength
                                player.on_ground = False
                                player.falling = False  # Ensure falling is reset
                                if player.sliding:
                                    player.sliding = False
                                    player.obstacle.height = player.jumping_height
                                    player.obstacle.width = player.jumping_width
                                game_started = True
                    elif boss_active:
                        near_ground = abs(player.obstacle.bottom - base.top) < 20
                        if player.on_ground or near_ground:
                            player.velocity = player.jump_strength
                            player.on_ground = False
                            player.falling = False  # Ensure falling is reset
                            if player.sliding:
                                player.sliding = False
                                player.obstacle.height = player.jumping_height
                                player.obstacle.width = player.jumping_width
                
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    slide_key_held = True
                    if not boss_active:
                        near_ground = abs(player.obstacle.bottom - base.top) < 10
                        if (player.on_ground or near_ground) and not player.sliding:
                            player.sliding = True
                            player.obstacle.height = player.sliding_height
                            player.obstacle.bottom = base.top
                    elif boss_active:
                        near_ground = abs(player.obstacle.bottom - base.top) < 10
                        if not player.sliding:
                            player.sliding = True
                            current_bottom = player.obstacle.bottom
                            current_centerx = player.obstacle.centerx
                            player.obstacle.height = player.sliding_height
                            player.obstacle.width = 175
                            player.obstacle.bottom = current_bottom
                            player.obstacle.centerx = current_centerx
                            if player.on_ground or near_ground:
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
        background_transition.draw(screen, background_image)
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

        background_transition.update(dt)
        above.update_transition(dt)
        base.update_transition(dt)
        
        if game_started:
            background_transition.draw(screen, background_image)
        else:
            screen.fill(BG)

        boss_defeat_in_progress = (boss is not None and boss.defeated)
        
        if game_started and not game_over and not boss_active and not boss_spawning and not boss_defeat_in_progress:
            score += dt*50

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
                boss_img = boss_image_paths[current_boss_index] if current_boss_index < len(boss_image_paths) else boss_image_paths[-1]
                boss = Boss(boss_img, base.top, current_boss_index)
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

        boss_defeat_complete = (boss is None or (boss is not None and not boss.active and not boss.defeated))
        
        if game_started and not boss_active and not boss_spawning and boss_defeat_complete:
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

        if boss is not None:
            boss.update(dt, player.obstacle)
            if boss.active or boss.defeated:
                boss.create(screen, dt)
            if boss.active and not boss.defeated:
                boss.draw_health_bar(screen)
            
            if boss.active and not boss.appearing and not boss.defeated and not game_over:
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
                
                for h_laser in boss.horizontal_lasers:
                    if h_laser.active:
                        laser_rects = h_laser.get_rects()
                        for laser_rect in laser_rects:
                            if player.obstacle.colliderect(laser_rect):
                                if not game_over:
                                    game_over = True
                
                for v_laser in boss.vertical_lasers:
                    if v_laser.active:
                        laser_rect = v_laser.get_rect()
                        if player.obstacle.colliderect(laser_rect):
                            if not game_over:
                                game_over = True
                
                for t_laser in boss.top_bottom_lasers:
                    if t_laser.active:
                        laser_rect = t_laser.get_rect()
                        if player.obstacle.colliderect(laser_rect):
                            if not game_over:
                                game_over = True
            
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
        
        can_shoot = True
        if boss_active and boss is not None:
            if boss.horizontal_laser_barrage_active:
                can_shoot = False
        
        if keys[pygame.K_f] and shoot_timer <= 0 and not game_over and not reloading and can_shoot:
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
            for bullet in list(bullets):
                bullet_destroyed = False
                for v_laser in boss.vertical_lasers:
                    if v_laser.active:
                        laser_rect = v_laser.get_rect()
                        if bullet.rect.colliderect(laser_rect):
                            bullet.kill()
                            bullet_destroyed = True
                            break
                
                if not bullet_destroyed:
                    for h_laser in boss.horizontal_lasers:
                        if h_laser.active:
                            laser_rects = h_laser.get_rects()
                            for laser_rect in laser_rects:
                                if bullet.rect.colliderect(laser_rect):
                                    bullet.kill()
                                    bullet_destroyed = True
                                    break
                            if bullet_destroyed:
                                break
                
                if not bullet_destroyed:
                    for t_laser in boss.top_bottom_lasers:
                        if t_laser.active:
                            laser_rect = t_laser.get_rect()
                            if bullet.rect.colliderect(laser_rect):
                                bullet.kill()
                                bullet_destroyed = True
                                break
                
                if not bullet_destroyed and boss.rect.colliderect(bullet.rect):
                    boss.hit(player, obstacles, base) 
                    bullet.kill()

        score_text = font.render(f"Score  : {str(int(score)).zfill(5)}", True, WHITE)
        screen.blit(score_text, (1050, 50))
        
        if reloading:
            ammo_text = font.render(f"Ammo : reloading.../{max_ammo}", True, (255, 200, 0))
        else:
            ammo_text = font.render(f"Ammo : {int(ammo)}/{max_ammo}", True, WHITE)
        screen.blit(ammo_text, (50, 50))
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
