from settings import * 
from sprites import * 
from groups import AllSprites
from support import * 
from timer import Timer
from random import randint
import sys
import math
import os

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Stage 2')
        self.clock = pygame.time.Clock()
        self.running = True
        
        current_dir = os.getcwd()
        if current_dir.endswith('stage 2'):
            self.base_path = '.'
        elif 'stage 2' in current_dir:
            self.base_path = '..'
        else:
            self.base_path = 'stage 2'
        
        self.score = 0
        try:
            self.font = pygame.font.Font(os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF'), 32)
            self.game_over_font = pygame.font.Font(os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF'), 64)
            self.title_font = pygame.font.Font(os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF'), 48)
        except:
            self.font = pygame.font.Font(None, 32)
            self.game_over_font = pygame.font.Font(None, 64)
            self.title_font = pygame.font.Font(None, 48)
        self.game_over = False

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.enemy_bullet_sprites = pygame.sprite.Group()

        self.load_assets()
        self.setup()

        self.bee_timer = Timer(1500, func=self.create_bee, autostart=True, repeat=True)
        
        self.lives = 3
        self.power = 1
        self.victory = False
        self.invulnerable_timer = Timer(2000)
        self.freeze_timer = Timer(1000)  # 1.5 second freeze timer
        self.pending_game_over = False  # Track if game over should happen after freeze
    
    def create_bee(self):
        TouhouBee(frames=self.bee_frames, 
                 pos=(WINDOW_WIDTH + 50, randint(50, WINDOW_HEIGHT - 200)),
                 groups=(self.all_sprites, self.enemy_sprites),
                 speed=randint(100, 200),
                 bullet_groups=self.enemy_bullet_sprites,
                 player=self.player)
            
    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        self.player_frames = import_folder(os.path.join(self.base_path, 'images'), 'player')
        self.bullet_surf = import_image(os.path.join(self.base_path, 'images'), 'gun', 'bullet')
        self.fire_surf = import_image(os.path.join(self.base_path, 'images'), 'gun', 'fire')
        
        self.bee_frames = import_folder(os.path.join(self.base_path, 'images'), 'enemies', 'bee')
        self.worm_frames = import_folder(os.path.join(self.base_path, 'images'), 'enemies', 'worm')
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        hearts_dir = os.path.join(base_dir, 'hearts')
        
        self.full_heart = pygame.image.load(os.path.join(hearts_dir, 'full_heart.png')).convert_alpha()
        self.empty_heart = pygame.image.load(os.path.join(hearts_dir, 'empety_heart.png')).convert_alpha()
        
        heart_size = (32, 32)
        self.full_heart = pygame.transform.scale(self.full_heart, heart_size)
        self.empty_heart = pygame.transform.scale(self.empty_heart, heart_size)

        self.audio = {
            'shoot': pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'shoot.wav')),
            'impact': pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'impact.ogg')),
            'music': pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'music.wav')),
        }
        
        for sound in self.audio.values():
            sound.set_volume(0.3)
            
        self.audio['music'].set_volume(0.2)
        self.audio['music'].play(loops=-1)

    def setup(self):
        tmx_map = load_pygame(os.path.join(self.base_path, 'data', 'maps', 'world.tmx'))
        self.level_width = tmx_map.width * tmx_map.tilewidth
        self.level_height = tmx_map.height * tmx_map.tileheight

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * tmx_map.tilewidth, y * tmx_map.tileheight), image, (self.all_sprites, self.collision_sprites))

        for object in tmx_map.get_layer_by_name('Entities'):
            if object.name == 'Player':
                self.player = Player(pos=(object.x, object.y),
                                   groups=self.all_sprites,
                                   collision_sprites=self.collision_sprites,
                                   frames=self.player_frames,
                                   create_bullet=self.create_bullet)
                self.ground_level = object.y
            elif object.name == 'Worm':
                Worm(self.worm_frames, pygame.FRect(object.x, object.y, object.width, object.height), (self.all_sprites, self.enemy_sprites))

    def collision(self):
        if self.bullet_sprites and self.enemy_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.audio['impact'].play()
                    for enemy in collision_sprites:
                        if hasattr(enemy, 'take_damage'):
                            if enemy.take_damage():
                                self.score += 100
                            else:
                                self.score += 10
                        else:
                            enemy.destroy()
                            self.score += 1
                    bullet.kill()
        
        if not self.invulnerable_timer and self.enemy_bullet_sprites:
            # Check for collision with any enemy bullet (red/orange dots)
            bullets_hit = pygame.sprite.spritecollide(self.player, self.enemy_bullet_sprites, False, pygame.sprite.collide_mask)
            if bullets_hit:
                self.player_hit()
                for bullet in bullets_hit:
                    bullet.kill()
        
        if not self.invulnerable_timer:
            collision_sprites = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collision_sprites:
                self.player_hit()
        else:
            # During invulnerability, destroy enemies on contact
            collision_sprites = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collision_sprites:
                for enemy in collision_sprites:
                    enemy.destroy()
                    self.score += 50  # Bonus points for destroying enemies while invulnerable
    
    def player_hit(self):
        self.lives -= 1
        self.invulnerable_timer.activate()
        self.freeze_timer.activate()  # Activate freeze effect
        self.audio['impact'].play()
        
        if self.lives <= 0:
            self.pending_game_over = True  # Mark for game over after freeze

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, 'white')
        self.display_surface.blit(score_text, (10, 10))
        
        max_lives = 3
        heart_spacing = 40
        heart_y = 10
        heart_start_x = WINDOW_WIDTH - (max_lives * heart_spacing) - 10  
        
        for i in range(max_lives):
            heart_x = heart_start_x + (i * heart_spacing)
            if i < self.lives:
                self.display_surface.blit(self.full_heart, (heart_x, heart_y))
            else:
                self.display_surface.blit(self.empty_heart, (heart_x, heart_y))
        
        power_text = self.font.render(f"Power: {self.power}", True, 'white')
        self.display_surface.blit(power_text, (10, 50))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            pygame.draw.circle(self.display_surface, (255, 255, 255), 
                             self.player.get_hitbox_center(), self.player.hitbox_radius, 1)

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        
        if self.victory:
            game_over_text = self.game_over_font.render("VICTORY!", True, (255, 215, 0))
            
            subtitle_text = self.title_font.render("Stage 2 Complete!", True, (100, 255, 100))
            subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80))
            self.display_surface.blit(subtitle_text, subtitle_rect)
            
            victory_msg = self.font.render("The Queen Bee has been defeated!", True, (200, 255, 200))
            msg_rect = victory_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            self.display_surface.blit(victory_msg, msg_rect)
            
            if hasattr(self, 'boss') and self.boss and not self.boss.alive():
                boss_msg = self.font.render("Boss Battle Complete!", True, (255, 255, 100))
                boss_rect = boss_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 10))
                self.display_surface.blit(boss_msg, boss_rect)
        else:
            game_over_text = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
            
            defeat_msg = self.font.render("The Queen Bee proved too powerful...", True, (255, 150, 150))
            defeat_rect = defeat_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            self.display_surface.blit(defeat_msg, defeat_rect)
            
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120))
        self.display_surface.blit(game_over_text, game_over_rect)
        
        final_score_text = self.title_font.render(f"Final Score: {self.score}", True, 'white')
        score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
        self.display_surface.blit(final_score_text, score_rect)
        
        performance_text = self.font.render(f"Lives Remaining: {self.lives}", True, (200, 200, 255))
        perf_rect = performance_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80))
        self.display_surface.blit(performance_text, perf_rect)
        
        restart_text = self.font.render("Press ESC to return to menu", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 140))
        self.display_surface.blit(restart_text, restart_rect)
        
        quit_text = self.font.render("Press Q to quit", True, (200, 200, 200))
        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 180))
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
                            self.running = False
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            
            if not self.game_over:
                self.bee_timer.update()
                self.invulnerable_timer.update()
                self.freeze_timer.update()
                
                # Check if game over should happen after freeze ends
                if self.pending_game_over and not self.freeze_timer:
                    self.game_over = True
                    self.pending_game_over = False
                
                # Only update game logic if not frozen
                if not self.freeze_timer:
                    self.all_sprites.update(dt)
                    self.enemy_bullet_sprites.update(dt)
                    self.collision()

                self.display_surface.fill(BG_COLOR)
                self.all_sprites.draw(self.player.rect.center)
                
                for bullet in self.enemy_bullet_sprites:
                    self.display_surface.blit(bullet.image, bullet.rect)
                
                self.draw_score()
                
                # Add freeze effect overlay
                if self.freeze_timer:
                    freeze_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    freeze_overlay.set_alpha(30)
                    freeze_overlay.fill((150, 200, 255))  # Light blue freeze effect
                    self.display_surface.blit(freeze_overlay, (0, 0))
                
                if self.invulnerable_timer and pygame.time.get_ticks() % 200 < 100:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    overlay.set_alpha(50)
                    overlay.fill((255, 0, 0))
                    self.display_surface.blit(overlay, (0, 0))
            else:
                self.draw_game_over()
            
            pygame.display.update()
        
        pygame.quit()
 
if __name__ == '__main__':
    game = Game()
    game.run()
