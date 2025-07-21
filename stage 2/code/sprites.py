from settings import * 
from timer import Timer
from math import sin, cos, atan2, sqrt
from random import randint, uniform
import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(topleft = pos)

class Bullet(Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(pos, surf, groups)
        
        # adjustment 
        self.image = pygame.transform.flip(self.image, direction == -1, False)

        # movement
        self.direction = direction
        self.speed = 850
    
    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt

class EnemyBullet(Sprite):
    def __init__(self, pos, target_pos, groups, speed=250, color=(255, 100, 100)):
        # Create an even larger bullet surface
        surf = pygame.Surface((20, 20))
        surf.fill(color)
        # Add a white center for visibility
        pygame.draw.circle(surf, (255, 255, 255), (10, 10), 6)
        super().__init__(pos, surf, groups)
        
        # Calculate direction to player
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        distance = sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
        else:
            self.velocity_x = 0
            self.velocity_y = speed
            
    def update(self, dt):
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt
        
        # Remove if off screen
        if (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT):
            self.kill()

class CircularBullet(Sprite):
    def __init__(self, pos, angle, groups, speed=180, color=(255, 150, 50)):
        # Create an even larger circular bullet
        surf = pygame.Surface((18, 18))
        surf.fill(color)
        # Add a darker center
        pygame.draw.circle(surf, (200, 100, 0), (9, 9), 5)
        super().__init__(pos, surf, groups)
        
        self.velocity_x = cos(angle) * speed
        self.velocity_y = sin(angle) * speed
        
    def update(self, dt):
        self.rect.x += self.velocity_x * dt
        self.rect.y += self.velocity_y * dt
        
        if (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT):
            self.kill()

class SpiralBullet(Sprite):
    def __init__(self, pos, angle, groups, speed=120, spiral_speed=0.03):
        # Create an even larger spiral bullet
        surf = pygame.Surface((16, 16))
        surf.fill((100, 255, 100))
        # Add a white dot in center
        pygame.draw.circle(surf, (255, 255, 255), (8, 8), 4)
        super().__init__(pos, surf, groups)
        
        self.angle = angle
        self.speed = speed
        self.spiral_speed = spiral_speed
        self.time = 0
        
    def update(self, dt):
        self.time += dt
        self.angle += self.spiral_speed
        
        self.rect.x += cos(self.angle) * self.speed * dt
        self.rect.y += sin(self.angle) * self.speed * dt
        
        if (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT):
            self.kill()

class Fire(Sprite):
    def __init__(self, surf, pos, groups, player):
        super().__init__(pos, surf, groups)
        self.player = player 
        self.flip = player.flip
        self.timer = Timer(100, autostart = True, func = self.kill)
        self.y_offset = pygame.Vector2(0,8)
        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset

    def update(self, _):
        self.timer.update()

        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset

        if self.flip != self.player.flip:
            self.kill()

class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frames, self.frame_index, self.animation_speed = frames, 0, 10
        super().__init__(pos, self.frames[self.frame_index], groups)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

class Enemy(AnimatedSprite):
    def __init__(self, frames, pos, groups):
        super().__init__(frames, pos, groups)
        self.death_timer = Timer(200, func = self.kill)
        self.health = 1

    def destroy(self):
        self.death_timer.activate()
        self.animation_speed = 0
        self.image = pygame.mask.from_surface(self.image).to_surface()
        self.image.set_colorkey('black')

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.destroy()

    def update(self, dt):
        self.death_timer.update()
        if not self.death_timer:
            self.move(dt)
            self.animate(dt)
        self.constraint()

class TouhouBee(Enemy):
    def __init__(self, frames, pos, groups, speed, bullet_groups, player):
        super().__init__(frames, pos, groups)
        self.speed = speed
        self.amplitude = randint(300, 400)
        self.frequency = randint(200, 400)
        self.bullet_groups = bullet_groups
        self.player = player
        self.shoot_timer = Timer(1800, autostart=True, repeat=True, func=self.shoot_pattern)
        self.pattern_type = randint(0, 2)
        
    def shoot_pattern(self):
        if self.pattern_type == 0:
            self.aimed_shot()
        elif self.pattern_type == 1:
            self.circular_pattern()
        else:
            self.triple_shot()
    
    def aimed_shot(self):
        EnemyBullet(self.rect.center, self.player.rect.center, self.bullet_groups)
    
    def circular_pattern(self):
        # Reduced from 6 to 5 bullets
        for i in range(5):
            angle = (i / 5) * 6.28  # 2*pi
            CircularBullet(self.rect.center, angle, self.bullet_groups)
    
    def triple_shot(self):
        player_angle = atan2(self.player.rect.centery - self.rect.centery, 
                           self.player.rect.centerx - self.rect.centerx)
        for offset in [-0.3, 0, 0.3]:
            EnemyBullet(self.rect.center, 
                       (self.rect.centerx + cos(player_angle + offset) * 100,
                        self.rect.centery + sin(player_angle + offset) * 100), 
                       self.bullet_groups)

    def move(self, dt):
        self.rect.x -= self.speed * dt
        self.rect.y += sin(pygame.time.get_ticks() / self.frequency) * self.amplitude * dt
    
    def update(self, dt):
        super().update(dt)
        self.shoot_timer.update()
    
    def constraint(self):
        if self.rect.right <= 0:
            self.kill()

class TouhouBoss(Enemy):
    def __init__(self, frames, pos, groups, bullet_groups, player):
        super().__init__(frames, pos, groups)
        self.health = 50
        self.max_health = 50
        self.bullet_groups = bullet_groups
        self.player = player
        self.speed = 60  # Slow speed for following player
        self.direction_y = 1
        self.name = "QUEEN BEE"  # Boss name
        
        # Make the boss bigger by scaling the image
        if frames:
            self.original_frames = frames
            self.frames = []
            for frame in frames:
                scaled_frame = pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2))
                self.frames.append(scaled_frame)
            # Update current image to scaled version
            self.image = self.frames[0]
            # Update rect to accommodate new size
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)
        
        # Attack patterns
        self.pattern_timer = Timer(3000, autostart=True, repeat=True, func=self.change_pattern)
        self.attack_timer = Timer(500, autostart=True, repeat=True, func=self.attack)
        self.current_pattern = 0
        self.pattern_phase = 0
        
    def change_pattern(self):
        self.current_pattern = (self.current_pattern + 1) % 4
        self.pattern_phase = 0
        
    def attack(self):
        if self.current_pattern == 0:
            self.spiral_pattern()
        elif self.current_pattern == 1:
            self.wave_pattern()
        elif self.current_pattern == 2:
            self.bullet_hell_pattern()
        else:
            self.homing_pattern()
        
        self.pattern_phase += 1
    
    def spiral_pattern(self):
        # Reduced from 4 to 3 bullets
        for i in range(3):
            angle = (self.pattern_phase * 0.1) + (i * 1.57)  # pi/2
            SpiralBullet(self.rect.center, angle, self.bullet_groups)
    
    def wave_pattern(self):
        # Reduced from 8 to 6 bullets
        for i in range(6):
            angle = (i / 6) * 6.28 + (self.pattern_phase * 0.2)
            CircularBullet(self.rect.center, angle, self.bullet_groups, speed=150)
    
    def bullet_hell_pattern(self):
        # Reduced dense bullet pattern from 10 to 8
        for i in range(8):
            angle = (i / 8) * 6.28
            CircularBullet(self.rect.center, angle, self.bullet_groups, 
                         speed=120, color=(255, 255, 100))
        
        # Keep aimed shots at 2
        if self.pattern_phase % 3 == 0:
            for i in range(2):
                EnemyBullet(self.rect.center, self.player.rect.center, 
                          self.bullet_groups, speed=200)
    
    def homing_pattern(self):
        # Reduced from 4 to 3 bullets
        if self.pattern_phase % 2 == 0:
            for _ in range(3):
                EnemyBullet(self.rect.center, self.player.rect.center, 
                          self.bullet_groups, speed=160)

    def animate(self, dt):
        if hasattr(self, 'frames') and self.frames:
            self.frame_index += self.animation_speed * dt
            self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        # Follow the player slowly
        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery
        
        # Calculate direction to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        
        # Normalize and apply slow movement
        distance = (dx**2 + dy**2)**0.5
        if distance > 0:
            # Move towards player but keep some distance
            if distance > 150:  # Only move if player is far enough
                move_x = (dx / distance) * self.speed * dt
                move_y = (dy / distance) * self.speed * dt
                
                self.rect.x += move_x
                self.rect.y += move_y
        
        # Add slight floating motion for visual appeal
        self.rect.y += sin(pygame.time.get_ticks() / 1000) * 20 * dt
    
    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.destroy()
            return True
        return False
    
    def update(self, dt):
        super().update(dt)
        self.pattern_timer.update()
        self.attack_timer.update()
    
    def constraint(self):
        # Keep boss on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH

class Bee(Enemy):
    def __init__(self, frames, pos, groups, speed):
        super().__init__(frames, pos, groups)
        self.speed = speed
        self.amplitude = randint(500,600)
        self.frequency = randint(300,600)

    def move(self, dt):
        self.rect.x -= self.speed * dt
        self.rect.y += sin(pygame.time.get_ticks() / self.frequency) * self.amplitude * dt
    
    def constraint(self):
        if self.rect.right <= 0:
            self.kill()

class Worm(Enemy):
    def __init__(self, frames, rect, groups):
        super().__init__(frames, rect.topleft, groups)
        self.rect.bottomleft = rect.bottomleft
        self.main_rect = rect
        self.speed = randint(160,200)
        self.direction = 1
    
    def move(self, dt):
        self.rect.x += self.direction * self.speed * dt

    def constraint(self):
        if not self.main_rect.contains(self.rect):
            self.direction *= -1
            self.frames = [pygame.transform.flip(surf, True, False) for surf in self.frames]

class Player(AnimatedSprite):
    def __init__(self, pos, groups, collision_sprites, frames, create_bullet):
        super().__init__(frames, pos, groups)
        self.flip = False
        self.create_bullet = create_bullet
    
        # movement & collision
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.speed = 300  # Slower for precision dodging
        self.gravity = 50
        self.on_floor = False

        # Double jump mechanics
        self.jump_count = 0
        self.max_jumps = 2
        self.jump_strength = -20
        self.space_pressed = False

        # timer
        self.shoot_timer = Timer(200)  # Faster shooting for bullet hell
        
        # Touhou-style hitbox
        self.hitbox_radius = 3
        
    def get_hitbox_center(self):
        return self.rect.center

    def input(self):
        keys = pygame.key.get_pressed()
        
        # More precise movement for dodging
        self.direction.x = 0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            
        # Slower focused movement (shift key)
        if keys[pygame.K_LSHIFT]:
            self.speed = 150
        else:
            self.speed = 300
            
        # Double jump mechanics
        if keys[pygame.K_SPACE]:
            if not self.space_pressed and self.jump_count < self.max_jumps:
                self.direction.y = self.jump_strength
                self.jump_count += 1
                self.space_pressed = True
        else:
            self.space_pressed = False
        
        # Shooting
        if keys[pygame.K_s] and not self.shoot_timer:
            self.create_bullet(self.rect.center, -1 if self.flip else 1)
            self.shoot_timer.activate()

    def move(self, dt):
        # horizontal
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        
        # vertical 
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.rect.right = sprite.rect.left
                    if self.direction.x < 0: self.rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0: self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.rect.top = sprite.rect.bottom
                    self.direction.y = 0

    def check_floor(self):
        bottom_rect = pygame.FRect((0,0), (self.rect.width, 2)).move_to(midtop = self.rect.midbottom)
        was_on_floor = self.on_floor
        self.on_floor = True if bottom_rect.collidelist([sprite.rect for sprite in self.collision_sprites]) >= 0 else False
        
        # Reset jump count when landing on floor
        if self.on_floor and not was_on_floor:
            self.jump_count = 0

    def animate(self, dt):
        if self.direction.x:
            self.frame_index += self.animation_speed * dt
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0

        self.frame_index = 1 if not self.on_floor else self.frame_index
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def update(self, dt):
        self.shoot_timer.update()
        self.check_floor()
        self.input()
        self.move(dt)
        self.animate(dt)