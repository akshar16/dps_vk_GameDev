from settings import * 
from sprites import * 
from groups import AllSprites
from support import * 
from timer import Timer
from random import randint
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('stage 1')
        self.clock = pygame.time.Clock()
        self.running = True
        
        # score system
        self.score = 0
        try:
            self.font = pygame.font.Font(join('..', 'fonts', '04B_30__.TTF'), 32)
            self.game_over_font = pygame.font.Font(join('..', 'fonts', '04B_30__.TTF'), 64)
            self.title_font = pygame.font.Font(join('..', 'fonts', '04B_30__.TTF'), 48)
        except:
            # Fallback to default fonts if custom font not found
            self.font = pygame.font.Font(None, 32)
            self.game_over_font = pygame.font.Font(None, 64)
            self.title_font = pygame.font.Font(None, 48)
        self.game_over = False

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load game 
        self.load_assets()
        self.setup()

        # timers 
        self.bee_timer = Timer(100, func = self.create_bee, autostart = True, repeat = True)
    
    def create_bee(self):
        Bee(frames = self.bee_frames, 
            pos = ((self.level_width + WINDOW_WIDTH),(randint(0,self.level_height))), 
            groups = (self.all_sprites, self.enemy_sprites),
            speed = randint(300,500))

    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        # graphics 
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')

        # sounds 
        self.audio = audio_importer('audio')

    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))
        
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames, self.create_bullet)
            if obj.name == 'Worm':
                Worm(self.worm_frames, pygame.FRect(obj.x, obj.y, obj.width, obj.height), (self.all_sprites, self.enemy_sprites))

        # self.audio['music'].play(loops = -1)

    def collision(self):
        # bullets -> enemies 
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                self.audio['impact'].play()
                bullet.kill()
                for sprite in sprite_collision:
                    sprite.destroy()
                    self.score += 1 # increase score when enemy is destroyed
        
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.game_over = True
            self.running = False

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, 'white')
        self.display_surface.blit(score_text, (10, 10))
    
    def draw_game_over(self):
        # Enhanced game over screen
        # Black overlay with transparency
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        
        # Game over title
        game_over_text = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
        self.display_surface.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.title_font.render(f"Final Score: {self.score}", True, 'white')
        score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
        self.display_surface.blit(final_score_text, score_rect)
        
        # Instructions
        restart_text = self.font.render("Press ESC to return to menu", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        self.display_surface.blit(restart_text, restart_rect)
        
        quit_text = self.font.render("Press Q to quit", True, (200, 200, 200))
        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 90))
        self.display_surface.blit(quit_text, quit_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False  # Return to menu
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            
            # update
            if not self.game_over:
                self.bee_timer.update()
                self.all_sprites.update(dt)
                self.collision()

                # draw 
                self.display_surface.fill(BG_COLOR)
                self.all_sprites.draw(self.player.rect.center)
                self.draw_score()  # draw score on top left
            else:
                self.draw_game_over()
            
            pygame.display.update()
        
        pygame.quit()
 
if __name__ == '__main__':
    game = Game()
    game.run() 