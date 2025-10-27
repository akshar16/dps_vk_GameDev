from settings import *
from math import atan2, degrees
import os


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups ):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(topleft = pos)


class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups, base_path='.'):
        self.player = player
        self.dist = 100
        self.player_dir = pygame.Vector2(1, 0)
        self.base_path = base_path

        super().__init__(groups)
        # Load and scale the gun to a larger size
        original_gun = pygame.image.load(os.path.join(self.base_path, 'images','gun', 'gun.png')).convert_alpha()
        gun_scale = 2  # 85% size (increased from 50%)
        self.gun_surface = pygame.transform.rotozoom(original_gun, 0, gun_scale)
        self.image = self.gun_surface
        self.rect = self.image.get_frect(center = player.rect.center + self.player_dir * self.dist)
        
        
    def getDirection(self):
        mouse_pos = pygame.mouse.get_pos()
        player_pos = pygame.Vector2(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.player_dir = (mouse_pos - player_pos).normalize() 
        
    def getRotation(self):
        angle = degrees(atan2(self.player_dir.x, self.player_dir.y)) - 90
        if self.player_dir.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surface, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surface, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False , True)
    def update(self, _):
        self.getRotation()
        self.getDirection()
        self.rect.center = self.player.rect.center + self.player_dir * self.dist
        
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self, surface, pos, direction, group):
        super().__init__(group)
        self.image = surface
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000 
        
        self.direction = direction
        self.speed = 1200
        
        
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
            
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, stationary=False):
        super().__init__(groups)
        self.player = player
        
        self.frames , self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6
        self.rect = self.image.get_frect(center = pos)
        self.hitbox = self.rect.inflate(-20, -40)
        
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 350
        self.stationary = stationary  # New parameter for stationary enemies
        
        self.death_time = 0
        self.death_duration = 400
        
        
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        
        
    def move(self, dt):
        # Freeze when in player's flashlight cone
        if getattr(self, 'frozen_by_light', False):
            return
        # Don't move if enemy is stationary
        if self.stationary:
            return
        
        # THEME: Invisibility - Can't chase invisible player
        if getattr(self.player, 'game', None):
            if getattr(self.player.game, 'player_invisible', False):
                # Player is invisible, wander randomly
                import random
                if not hasattr(self, 'wander_timer'):
                    self.wander_timer = 0
                self.wander_timer += dt
                if self.wander_timer > 2:  # Change direction every 2 seconds
                    self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    if self.direction.length() > 0:
                        self.direction = self.direction.normalize()
                    self.wander_timer = 0
                
                self.hitbox.x += self.direction.x * dt * self.speed * 0.3  # Slower wandering
                self.collision("horizontal")
                self.hitbox.y += self.direction.y * dt * self.speed * 0.3
                self.collision("vertical")
                self.rect.center = self.hitbox.center
                return
            
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize() 

        self.hitbox.x += self.direction.x * dt * self.speed
        self.collision("horizontal")
        self.hitbox.y += self.direction.y * dt * self.speed
        self.collision("vertical")
        self.rect.center = self.hitbox.center

    def collision(self, direction):
         for sprite in self.collision_sprites:
            if self.hitbox.colliderect(sprite.rect):
                if direction == "vertical" :
                    if self.direction.y > 0 : self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0 : self.hitbox.top = sprite.rect.bottom
                if direction == "horizontal":
                    if self.direction.x > 0 : self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0 : self.hitbox.left = sprite.rect.right
    def destroy(self):
        self.death_time = pygame.time.get_ticks()
        surface = pygame.mask.from_surface(self.frames[0]).to_surface()
        surface.set_colorkey("black")
        self.image = surface
    
    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()
    def update(self , dt):
        if self.death_time == 0:
            self.animate(dt)
            self.move(dt)
        else:
            self.death_timer()
            
            
class Shop(pygame.sprite.Sprite):
    """Idle, animated shop entity (no collision)."""
    def __init__(self, pos, groups, base_path='.', collision_group=None):  # collision_group ignored
        super().__init__(groups)
        self.base_path = base_path
        # Load frames from images/shop
        folder = os.path.join(self.base_path, 'images', 'shop')
        file_names = []
        for _, _, names in os.walk(folder):
            file_names.extend([n for n in names if n.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])
            break
        def sort_key(name: str):
            stem = name.rsplit('.', 1)[0]
            return (0, int(stem)) if stem.isdigit() else (1, stem.lower())
        file_names = sorted(file_names, key=sort_key)
        loaded = [pygame.image.load(os.path.join(folder, n)).convert_alpha() for n in file_names]
        if not loaded:
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(surf, (200, 180, 40), surf.get_rect(), 2)
            loaded = [surf]

        # Simple, visible scaling (adjustable here)
        scale_factor = 3
        self.frames = [pygame.transform.smoothscale(img, (max(1, img.get_width()*scale_factor),
                                                          max(1, img.get_height()*scale_factor)))
                       for img in loaded]

        self.frame_index = 0
        self.animation_speed = 6
        self.image = self.frames[self.frame_index]

        # Anchor by feet to the Tiled object pos
        self.anchor_pos = (pos[0], pos[1])
        self.rect = self.image.get_frect()
        self.rect.midbottom = self.anchor_pos
        # No 'ground' attribute so it's treated as an object sprite

    def update(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        # Re-apply feet anchor every frame
        new_rect = self.image.get_frect()
        new_rect.midbottom = self.anchor_pos
        self.rect = new_rect

