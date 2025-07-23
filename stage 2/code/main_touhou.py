from settings import * 
from sprites import * 
from groups import AllSprites
from support import * 
from timer import Timer
from random import randint
import sys
import math

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Stage 2')
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(True)
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        try:
            self.font = pygame.font.Font(join('..', 'fonts', '04B_30__.TTF'), 32)
            self.game_over_font = pygame.font.Font(join('..', 'fonts', '04B_30__.TTF'), 64)
            self.title_font = pygame.font.Font(join('..', 'fonts', '04B_30__.TTF'), 48)
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
        self.enemy_spawn_timer = Timer(2000, func=self.create_touhou_enemy, autostart=True, repeat=True)
        self.boss_spawn_timer = Timer(30000, func=self.spawn_boss, autostart=True)
        self.boss_spawned = False
        self.boss = None
        self.lives = 3
        self.power = 1
        self.invulnerable_timer = Timer(2000)
    
    def create_touhou_enemy(self):
        if not self.boss_spawned:
            enemy_type = randint(0, 1)
            print(f"Spawning enemy type: {enemy_type}")
            if enemy_type == 0:
                TouhouBee(frames=self.bee_frames, 
                         pos=(WINDOW_WIDTH + 50, randint(50, WINDOW_HEIGHT - 200)),
                         groups=(self.all_sprites, self.enemy_sprites),
                         speed=randint(100, 200),
                         bullet_groups=self.enemy_bullet_sprites,
                         player=self.player)
                print("Spawned TouhouBee")
            else:
                worm_rect = pygame.Rect(200, WINDOW_HEIGHT - 150, 300, 50)
                print(f"Creating worm at rect: {worm_rect}")
                worm = Worm(frames=self.worm_frames, 
                           rect=worm_rect,
                           groups=(self.all_sprites, self.enemy_sprites))
                print(f"Worm created: {worm}")
                print(f"Total enemies: {len(self.enemy_sprites)}")
                print(f"Total sprites: {len(self.all_sprites)}")
    
    def spawn_boss(self):
        if not self.boss_spawned:
            self.boss = TouhouBoss(frames=self.bee_frames,
                                 pos=(WINDOW_WIDTH - 200, 100),
                                 groups=(self.all_sprites, self.enemy_sprites),
                                 bullet_groups=self.enemy_bullet_sprites,
                                 player=self.player)
            self.boss_spawned = True

    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')
        print(f"Loaded {len(self.bee_frames)} bee frames")
        print(f"Loaded {len(self.worm_frames)} worm frames")
        self.audio = {
            'shoot': pygame.mixer.Sound(join('audio', 'shoot.wav')),
            'impact': pygame.mixer.Sound(join('audio', 'impact.ogg')),
        }
        for sound in self.audio.values():
            sound.set_volume(0.3)

    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx'))
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
            player_center = self.player.get_hitbox_center()
            for bullet in self.enemy_bullet_sprites:
                bullet_center = bullet.rect.center
                distance = math.sqrt((player_center[0] - bullet_center[0])**2 + 
                                   (player_center[1] - bullet_center[1])**2)
                if distance < self.player.hitbox_radius + 3:
                    self.player_hit()
                    bullet.kill()
                    break
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
            self.running = False

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, 'white')
        self.display_surface.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, 'white')
        self.display_surface.blit(lives_text, (10, 50))
        power_text = self.font.render(f"Power: {self.power}", True, 'white')
        self.display_surface.blit(power_text, (10, 90))
        if self.boss and self.boss.alive():
            boss_health_percent = self.boss.health / self.boss.max_health
            health_bar_width = 400
            health_bar_height = 20
            pygame.draw.rect(self.display_surface, (100, 0, 0), 
                           (WINDOW_WIDTH//2 - health_bar_width//2, 20, health_bar_width, health_bar_height))
            pygame.draw.rect(self.display_surface, (255, 0, 0), 
                           (WINDOW_WIDTH//2 - health_bar_width//2, 20, 
                            health_bar_width * boss_health_percent, health_bar_height))
            boss_text = self.font.render("BOSS", True, 'yellow')
            boss_rect = boss_text.get_rect(center=(WINDOW_WIDTH//2, 10))
            self.display_surface.blit(boss_text, boss_rect)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            pygame.draw.circle(self.display_surface, (255, 255, 255), 
                             self.player.get_hitbox_center(), self.player.hitbox_radius, 1)

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))
        game_over_text = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
        self.display_surface.blit(game_over_text, game_over_rect)
        final_score_text = self.title_font.render(f"Final Score: {self.score}", True, 'white')
        score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
        self.display_surface.blit(final_score_text, score_rect)
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
                    if event.key == pygame.K_ESCAPE:
                        pygame.event.set_grab(False)
                        self.running = False
                    elif event.key == pygame.K_q:
                        pygame.event.set_grab(False)
                        pygame.quit()
                        sys.exit()
                    elif self.game_over:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            if not self.game_over:
                self.enemy_spawn_timer.update()
                self.boss_spawn_timer.update()
                self.invulnerable_timer.update()
                self.all_sprites.update(dt)
                self.enemy_bullet_sprites.update(dt)
                self.collision()
                self.display_surface.fill(BG_COLOR)
                self.all_sprites.draw(self.player.rect.center)
                for bullet in self.enemy_bullet_sprites:
                    self.display_surface.blit(bullet.image, bullet.rect)
                self.draw_score()
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
