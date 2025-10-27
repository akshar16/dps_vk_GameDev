from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display = pygame.display.get_surface()
        self.offset = pygame.Vector2(0,0)
        self.boundary_rect = None  # Set by game

    def draw(self, target_pos):
        
        groundSprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        objectSprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        
        # Constrain camera to boundary (only if map is larger than viewport)
        if self.boundary_rect:
            # Calculate what the camera can see
            cam_left = -self.offset.x
            cam_right = -self.offset.x + WINDOW_WIDTH
            cam_top = -self.offset.y
            cam_bottom = -self.offset.y + WINDOW_HEIGHT
            
            # Only constrain if map is larger than window in that dimension
            if self.boundary_rect.width >= WINDOW_WIDTH:
                if cam_left < self.boundary_rect.left:
                    self.offset.x = -self.boundary_rect.left
                if cam_right > self.boundary_rect.right:
                    self.offset.x = -(self.boundary_rect.right - WINDOW_WIDTH)
            
            if self.boundary_rect.height >= WINDOW_HEIGHT:
                if cam_top < self.boundary_rect.top:
                    self.offset.y = -self.boundary_rect.top
                if cam_bottom > self.boundary_rect.bottom:
                    self.offset.y = -(self.boundary_rect.bottom - WINDOW_HEIGHT)
        
        for layers in [groundSprites, objectSprites]:
            for sprite in sorted(layers, key=lambda sprite: sprite.rect.centery):
                # Check if this is an enemy and if enemies are currently invisible (blinking)
                is_enemy = hasattr(sprite, 'death_time')
                
                # Skip drawing invisible enemies during blink phase
                if is_enemy and hasattr(self, 'enemy_visible') and not self.enemy_visible:
                    continue
                
                self.display.blit(sprite.image, sprite.rect.topleft + self.offset)