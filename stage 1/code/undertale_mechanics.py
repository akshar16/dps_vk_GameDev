import pygame
from settings import *
from random import randint, choice
from math import sin, cos, atan2, sqrt
import time

class UndertaleGame:
    def __init__(self, main_game):
        self.main_game = main_game
        self.state = "EXPLORATION"
        self.battle_box = pygame.Rect(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 100, 400, 200)
        self.soul_pos = [self.battle_box.centerx, self.battle_box.centery]
        self.soul_size = 16
        self.soul_speed = 200
        self.current_enemy = None
        self.enemy_hp = 100
        self.enemy_max_hp = 100
        self.player_hp = 20
        self.player_max_hp = 20
        self.battle_phase = "MENU"
        self.menu_selection = 0
        self.menu_options = ["FIGHT", "ACT", "ITEM", "MERCY"]
        self.attack_timer = 0
        self.attack_duration = 5000
        self.bullets = []
        self.dialogue_text = ""
        self.dialogue_visible = False
        self.dialogue_timer = 0
        self.enemy_mercy_points = 0
        self.enemy_can_spare = False
        self.colors = {
            'white': (255, 255, 255),
            'blue': (100, 150, 255),
            'orange': (255, 150, 100),
            'green': (100, 255, 100),
            'red': (255, 100, 100)
        }

class UndertaleSoul:
    def __init__(self, pos, color=(255, 0, 0)):
        self.pos = list(pos)
        self.color = color
        self.size = 16
        self.speed = 200
        self.invulnerable = False
        self.invuln_timer = 0
        
    def update(self, dt, battle_box):
        if self.invulnerable:
            self.invuln_timer -= dt * 1000
            if self.invuln_timer <= 0:
                self.invulnerable = False
        keys = pygame.key.get_pressed()
        move_speed = self.speed * dt
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pos[0] -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pos[0] += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pos[1] -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pos[1] += move_speed
        self.pos[0] = max(battle_box.left + self.size//2, 
                         min(battle_box.right - self.size//2, self.pos[0]))
        self.pos[1] = max(battle_box.top + self.size//2, 
                         min(battle_box.bottom - self.size//2, self.pos[1]))
    
    def get_rect(self):
        return pygame.Rect(self.pos[0] - self.size//2, self.pos[1] - self.size//2, 
                          self.size, self.size)
    
    def take_damage(self):
        if not self.invulnerable:
            self.invulnerable = True
            self.invuln_timer = 1000
            return True
        return False
    
    def draw(self, surface):
        if self.invulnerable and int(pygame.time.get_ticks() / 100) % 2:
            return
        points = [
            (self.pos[0], self.pos[1] - self.size//2),
            (self.pos[0] + self.size//2, self.pos[1]),
            (self.pos[0], self.pos[1] + self.size//2),
            (self.pos[0] - self.size//2, self.pos[1])
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)

class UndertaleBullet:
    def __init__(self, pos, velocity, color='white', bullet_type='normal'):
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.color = color
        self.size = 12
        self.bullet_type = bullet_type
        self.alive = True
        if bullet_type == 'blue':
            self.damage_on_move = True
        elif bullet_type == 'orange':
            self.damage_on_still = True
        else:
            self.damage_on_move = False
            self.damage_on_still = False
    
    def update(self, dt, battle_box):
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt
        if (self.pos[0] < battle_box.left - 50 or self.pos[0] > battle_box.right + 50 or
            self.pos[1] < battle_box.top - 50 or self.pos[1] > battle_box.bottom + 50):
            self.alive = False
    
    def get_rect(self):
        return pygame.Rect(self.pos[0] - self.size//2, self.pos[1] - self.size//2,
                          self.size, self.size)
    
    def draw(self, surface):
        color_map = {
            'white': (255, 255, 255),
            'blue': (100, 150, 255),
            'orange': (255, 150, 100),
            'green': (100, 255, 100),
            'red': (255, 100, 100)
        }
        bullet_color = color_map.get(self.color, (255, 255, 255))
        pygame.draw.circle(surface, bullet_color, (int(self.pos[0]), int(self.pos[1])), self.size//2)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.pos[0]), int(self.pos[1])), self.size//2, 2)

class UndertaleEnemy:
    def __init__(self, name, hp, attacks):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attacks = attacks
        self.current_attack = 0
        self.mercy_points = 0
        self.can_spare = False
        self.dialogue_lines = [
            f"* {name} blocks the way!",
            f"* {name} is preparing an attack.",
            f"* {name} looks tired.",
            f"* {name} doesn't want to fight anymore."
        ]
        self.act_options = ["Check", "Talk", "Compliment"]
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
    
    def add_mercy(self, points):
        self.mercy_points += points
        if self.mercy_points >= 100:
            self.can_spare = True
    
    def get_dialogue(self):
        if self.can_spare:
            return self.dialogue_lines[3]
        elif self.hp < self.max_hp * 0.3:
            return self.dialogue_lines[2]
        else:
            return choice(self.dialogue_lines[:2])

def create_attack_pattern_1(battle_box, bullets):
    for i in range(5):
        pos = [battle_box.left - 20, battle_box.top + i * 40]
        velocity = [150, 0]
        bullets.append(UndertaleBullet(pos, velocity, 'white'))
        pos = [battle_box.right + 20, battle_box.top + i * 40]
        velocity = [-150, 0]
        bullets.append(UndertaleBullet(pos, velocity, 'white'))

def create_attack_pattern_2(battle_box, bullets):
    center = battle_box.center
    for i in range(8):
        angle = (i / 8) * 6.28
        pos = [center[0], center[1]]
        velocity = [cos(angle) * 100, sin(angle) * 100]
        bullets.append(UndertaleBullet(pos, velocity, 'blue'))

def create_attack_pattern_3(battle_box, bullets):
    for i in range(3):
        pos = [battle_box.left + i * 100, battle_box.top - 20]
        velocity = [0, 80]
        bullets.append(UndertaleBullet(pos, velocity, 'blue', 'blue'))
        pos = [battle_box.left + 50 + i * 100, battle_box.top - 20]
        velocity = [0, 120]
        bullets.append(UndertaleBullet(pos, velocity, 'orange', 'orange'))

ATTACK_PATTERNS = [
    create_attack_pattern_1,
    create_attack_pattern_2,
    create_attack_pattern_3
]
