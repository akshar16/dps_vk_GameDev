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
        pygame.display.set_caption('Touhou-Style Stage 2')
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Determine the correct base path for assets
        current_dir = os.getcwd()
        if current_dir.endswith('stage 2'):
            # Running from stage 2 directory
            self.base_path = '.'
        elif 'stage 2' in current_dir:
            # Running from stage 2/code directory
            self.base_path = '..'
        else:
            # Running from parent directory (e.g., from start screen)
            self.base_path = 'stage 2'

        # score system
        self.score = 0
        try:
            self.font = pygame.font.Font(os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF'), 32)
            self.game_over_font = pygame.font.Font(os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF'), 64)
            self.title_font = pygame.font.Font(os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF'), 48)
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
        self.enemy_bullet_sprites = pygame.sprite.Group()  # New group for enemy bullets

        # load game 
        self.load_assets()
        self.setup()

        # Touhou-style timers - faster enemy spawning
        self.enemy_spawn_timer = Timer(1200, func=self.create_touhou_enemy, autostart=True, repeat=True)
        self.fast_spawn_timer = Timer(800, func=self.create_fast_enemy, autostart=True, repeat=True)  # Additional spawner
        
        # Game state
        self.lives = 3
        self.power = 1
        self.victory = False  # Track if player won
        self.invulnerable_timer = Timer(2000)  # Invulnerability after getting hit
    
    def create_touhou_enemy(self):
        # Spawn multiple enemies at once
        num_enemies = randint(1, 3)  # Spawn 1-3 enemies each time
        
        for _ in range(num_enemies):
            enemy_type = randint(0, 2)  # Increased variety
            
            if enemy_type == 0:
                # TouhouBee
                TouhouBee(frames=self.bee_frames, 
                         pos=(WINDOW_WIDTH + randint(50, 150), randint(50, WINDOW_HEIGHT - 200)),
                         groups=(self.all_sprites, self.enemy_sprites),
                         speed=randint(80, 180),
                         bullet_groups=self.enemy_bullet_sprites,
                         player=self.player)
            elif enemy_type == 1:
                # Regular Bee (faster, no bullets)
                Bee(frames=self.bee_frames,
                    pos=(WINDOW_WIDTH + randint(50, 150), randint(50, WINDOW_HEIGHT - 200)),
                    groups=(self.all_sprites, self.enemy_sprites),
                    speed=randint(200, 300))
            else:
                # Another TouhouBee with different pattern
                bee = TouhouBee(frames=self.bee_frames, 
                               pos=(WINDOW_WIDTH + randint(50, 150), randint(50, WINDOW_HEIGHT - 200)),
                               groups=(self.all_sprites, self.enemy_sprites),
                               speed=randint(100, 220),
                               bullet_groups=self.enemy_bullet_sprites,
                               player=self.player)
                # Force different pattern
                bee.pattern_type = randint(0, 2)
    
    def create_fast_enemy(self):
        # Spawn quick enemies from different sides
        side = randint(0, 3)
        
        if side == 0:  # Right side
            pos = (WINDOW_WIDTH + 30, randint(100, WINDOW_HEIGHT - 300))
        elif side == 1:  # Top
            pos = (randint(100, WINDOW_WIDTH - 100), -30)
        elif side == 2:  # Left side (occasionally)
            pos = (-30, randint(100, WINDOW_HEIGHT - 300))
        else:  # Bottom
            pos = (randint(100, WINDOW_WIDTH - 100), WINDOW_HEIGHT + 30)
        
        # Create fast moving regular bee
        Bee(frames=self.bee_frames,
            pos=pos,
            groups=(self.all_sprites, self.enemy_sprites),
            speed=randint(250, 400))
            
    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        # graphics 
        self.player_frames = import_folder(os.path.join(self.base_path, 'images'), 'player')
        self.bullet_surf = import_image(os.path.join(self.base_path, 'images'), 'gun', 'bullet')
        self.fire_surf = import_image(os.path.join(self.base_path, 'images'), 'gun', 'fire')
        
        # enemy frames
        self.bee_frames = import_folder(os.path.join(self.base_path, 'images'), 'enemies', 'bee')
        self.worm_frames = import_folder(os.path.join(self.base_path, 'images'), 'enemies', 'worm')
        
        # heart graphics for lives (using absolute path)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        hearts_dir = os.path.join(base_dir, 'hearts')
        
        self.full_heart = pygame.image.load(os.path.join(hearts_dir, 'full_heart.png')).convert_alpha()
        self.empty_heart = pygame.image.load(os.path.join(hearts_dir, 'empety_heart.png')).convert_alpha()
        
        # Scale hearts to appropriate size
        heart_size = (32, 32)
        self.full_heart = pygame.transform.scale(self.full_heart, heart_size)
        self.empty_heart = pygame.transform.scale(self.empty_heart, heart_size)

        # audio 
        self.audio = {
            'shoot': pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'shoot.wav')),
            'impact': pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'impact.ogg')),
            'music': pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'music.wav')),
        }
        
        # Set volume
        for sound in self.audio.values():
            sound.set_volume(0.3)
            
        # Start background music
        self.audio['music'].set_volume(0.2)  # Lower volume for background music
        self.audio['music'].play(loops=-1)  # Loop indefinitely

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

    def collision(self):
        # Player bullets hitting enemies
        if self.bullet_sprites and self.enemy_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.audio['impact'].play()
                    for enemy in collision_sprites:
                        if hasattr(enemy, 'take_damage'):
                            if enemy.take_damage():  # Enemy defeated
                                self.score += 100
                            else:
                                self.score += 10
                        else:
                            enemy.destroy()
                            self.score += 1
                    bullet.kill()
        
        # Enemy bullets hitting player (Touhou-style precise hitbox)
        if not self.invulnerable_timer and self.enemy_bullet_sprites:
            player_center = self.player.get_hitbox_center()
            for bullet in self.enemy_bullet_sprites:
                bullet_center = bullet.rect.center
                distance = math.sqrt((player_center[0] - bullet_center[0])**2 + 
                                   (player_center[1] - bullet_center[1])**2)
                
                if distance < self.player.hitbox_radius + 3:  # Small collision
                    self.player_hit()
                    bullet.kill()
                    break
        
        # Enemy collision with player
        if not self.invulnerable_timer:
            collision_sprites = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collision_sprites:
                self.player_hit()
    
    def player_hit(self):
        self.lives -= 1
        self.invulnerable_timer.activate()
        self.audio['impact'].play()
        
        if self.lives <= 0:
            self.game_over = True
            # Don't set self.running = False here so the end screen can be displayed

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, 'white')
        self.display_surface.blit(score_text, (10, 10))
        
        # Draw hearts for lives in top-right corner
        max_lives = 3
        heart_spacing = 40
        heart_y = 10
        heart_start_x = WINDOW_WIDTH - (max_lives * heart_spacing) - 10  # Right side with padding
        
        for i in range(max_lives):
            heart_x = heart_start_x + (i * heart_spacing)
            if i < self.lives:
                # Draw full heart
                self.display_surface.blit(self.full_heart, (heart_x, heart_y))
            else:
                # Draw empty heart
                self.display_surface.blit(self.empty_heart, (heart_x, heart_y))
        
        # Draw power below score (left side)
        power_text = self.font.render(f"Power: {self.power}", True, 'white')
        self.display_surface.blit(power_text, (10, 50))
        
        # Draw player hitbox when focused (shift key)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            pygame.draw.circle(self.display_surface, (255, 255, 255), 
                             self.player.get_hitbox_center(), self.player.hitbox_radius, 1)

    def draw_game_over(self):
        # Enhanced game over screen with black overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        
        # Game over title - different for victory vs defeat
        if self.victory:
            game_over_text = self.game_over_font.render("VICTORY!", True, (255, 215, 0))
            
            # Victory subtitle
            subtitle_text = self.title_font.render("Stage 2 Complete!", True, (100, 255, 100))
            subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80))
            self.display_surface.blit(subtitle_text, subtitle_rect)
            
            # Victory message
            victory_msg = self.font.render("The Queen Bee has been defeated!", True, (200, 255, 200))
            msg_rect = victory_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            self.display_surface.blit(victory_msg, msg_rect)
            
            # Additional victory details
            if hasattr(self, 'boss') and self.boss and not self.boss.alive():
                boss_msg = self.font.render("Boss Battle Complete!", True, (255, 255, 100))
                boss_rect = boss_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 10))
                self.display_surface.blit(boss_msg, boss_rect)
        else:
            game_over_text = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
            
            # Defeat message
            defeat_msg = self.font.render("The Queen Bee proved too powerful...", True, (255, 150, 150))
            defeat_rect = defeat_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            self.display_surface.blit(defeat_msg, defeat_rect)
            
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120))
        self.display_surface.blit(game_over_text, game_over_rect)
        
        # Final score - prominently displayed
        final_score_text = self.title_font.render(f"Final Score: {self.score}", True, 'white')
        score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
        self.display_surface.blit(final_score_text, score_rect)
        
        # Performance stats
        performance_text = self.font.render(f"Lives Remaining: {self.lives}", True, (200, 200, 255))
        perf_rect = performance_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80))
        self.display_surface.blit(performance_text, perf_rect)
        
        # Instructions with better spacing
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
                            self.running = False  # Return to menu
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            
            # update
            if not self.game_over:
                self.enemy_spawn_timer.update()
                self.fast_spawn_timer.update()
                self.invulnerable_timer.update()
                
                self.all_sprites.update(dt)
                self.enemy_bullet_sprites.update(dt)
                self.collision()

                # draw 
                self.display_surface.fill(BG_COLOR)
                self.all_sprites.draw(self.player.rect.center)
                
                # Draw enemy bullets
                for bullet in self.enemy_bullet_sprites:
                    self.display_surface.blit(bullet.image, bullet.rect)
                
                self.draw_score()
                
                # Flash effect when invulnerable
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
