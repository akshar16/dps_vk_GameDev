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
        self.gun_surface = pygame.image.load(os.path.join(self.base_path, 'images','gun', 'gun.png')).convert_alpha()
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
        # Don't move if enemy is stationary
        if self.stationary:
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
            
            
        