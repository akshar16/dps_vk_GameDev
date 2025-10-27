from settings import *
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, base_path='.'):
        super().__init__(groups)
        self.base_path = base_path
        self.game = None  # Reference to game for theme mechanics
        self.frames()
        self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(os.path.join(self.base_path, 'images', 'player','down','0.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.hitbox = self.rect.inflate(-60, -90) 
        
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites
        self.boundary_rect = None  # Set by game after setup

    def frames(self):
        self.frames = {'left':[], 'right':[], 'up':[], 'down':[]}
        for state in self.frames.keys():
            for folder_path, sub_folders, image_names in walk(os.path.join(self.base_path, 'images', 'player', state)):
                if image_names:
                    for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
                        full_path = os.path.join(folder_path, image_name)
                        surface = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surface)


    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int (keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def animate(self, dt):
        
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
            
        self.frame_index += 5  * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index)%len(self.frames[self.state])]

    def move(self, dt):
        self.hitbox.y += self.direction.y * dt * self.speed
        self.collision("vertical")
        self.hitbox.x += self.direction.x * dt * self.speed
        self.collision("horizontal")
        
        # Constrain to boundary
        if self.boundary_rect:
            if self.hitbox.left < self.boundary_rect.left:
                self.hitbox.left = self.boundary_rect.left
            if self.hitbox.right > self.boundary_rect.right:
                self.hitbox.right = self.boundary_rect.right
            if self.hitbox.top < self.boundary_rect.top:
                self.hitbox.top = self.boundary_rect.top
            if self.hitbox.bottom > self.boundary_rect.bottom:
                self.hitbox.bottom = self.boundary_rect.bottom

        self.rect.center = self.hitbox.center
    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if self.hitbox.colliderect(sprite.rect):
                if direction == "vertical" :
                    if self.direction.y > 0 : self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0 : self.hitbox.top = sprite.rect.bottom
                if direction == "horizontal":
                    if self.direction.x > 0 : self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0 : self.hitbox.left = sprite.rect.right