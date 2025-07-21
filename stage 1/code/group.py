from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display = pygame.display.get_surface()
        self.offset = pygame.Vector2(0,0)

    def draw(self, target_pos):
        
        groundSprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        objectSprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        for layers in [groundSprites, objectSprites]:
            for sprite in sorted(layers, key=lambda sprite: sprite.rect.centery):
                self.display.blit(sprite.image, sprite.rect.topleft + self.offset)