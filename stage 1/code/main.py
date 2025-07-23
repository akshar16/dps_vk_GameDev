from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from group import AllSprites
from random import randint, choice
from undertale_mechanics import *
from npc_system import *
from timer import Timer
import sys
import os

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Survivor")
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(True)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.base_path = '..'

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        
        self.game_mode = "INTRO"
        self.story_mode = False
        self.undertale_system = None
        self.soul = None
        self.undertale_bullets = []
        self.battle_box = pygame.Rect(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 100, 400, 200)
        self.current_undertale_enemy = None
        self.battle_phase = "MENU"
        self.menu_selection = 0
        self.menu_options = ["ATTACK", "TALK", "HEAL", "SPARE"]
        self.attack_timer = 0
        self.attack_duration = 3000
        self.dialogue_text = ""
        self.dialogue_timer = 0
        self.player_hp = 20
        self.player_max_hp = 20
        
        self.npc_sprites = pygame.sprite.Group()
        self.npc_dialogue = NPCDialogue(self)
        self.intro_complete = False
        
        self.can_shoot = True
        self.gun_cd = 100
        self.shoot_time = 0
        
        self.score = 0
        self.victory = False
        
        self.story_enemies_spawned = 0
        self.story_enemies_killed = 0
        self.max_story_enemies = 10
        self.story_message_shown = False
        self.story_complete = False
        self.undertale_defeat = False
        try:
            font_path = os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF')
            print(f"Loading custom font from: {font_path}")
            self.font = pygame.font.Font(font_path, 32)
            self.game_over_font = pygame.font.Font(font_path, 64)
            self.title_font = pygame.font.Font(font_path, 48)
            print("Custom font loaded successfully!")
        except Exception as e:
            print(f"Failed to load custom font: {e}")
            self.font = pygame.font.Font(None, 32)
            self.game_over_font = pygame.font.Font(None, 64)
            self.title_font = pygame.font.Font(None, 48)
            print("Using default fonts as fallback")
        self.game_over = False
        self.freeze_timer = Timer(1000)  # 1 second freeze timer
        self.pending_game_over = False  # Track if game over should happen after freeze
        
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.enemy_position = []
        
        try:
            self.shoot_sound = pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'shoot.wav'))
            self.shoot_sound.set_volume(0.4)
        except Exception as e:
            print(f"Could not load shoot sound: {e}")
            self.shoot_sound = None
            
        try:
            self.impact_sound = pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'impact.ogg'))
        except Exception as e:
            print(f"Could not load impact sound: {e}")
            self.impact_sound = None
            
        try:
            self.music = pygame.mixer.Sound(os.path.join(self.base_path, 'audio', 'music.wav'))
            self.music.set_volume(0.2)
            self.music.play(loops = -1)
        except Exception as e:
            print(f"Could not load background music: {e}")
            self.music = None

        self.load_images()
        self.setup()
    
    def load_images(self):
        self.bullet_surface = pygame.image.load(os.path.join(self.base_path, 'images', 'gun', 'bullet.png')).convert_alpha()
        folders = list(walk(os.path.join(self.base_path, 'images','enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, image_names in walk(os.path.join(self.base_path, 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
                    full_path = os.path.join(folder_path, image_name)
                    surface = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surface)
    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            if self.shoot_sound:
                self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_dir *  50
            Bullet(self.bullet_surface, pos, self.gun.player_dir, (self.all_sprites,self.bullet_sprites))
            self.can_shoot = False
            self.gun_time = pygame.time.get_ticks()
           
    def setup(self):
         map = load_pygame(os.path.join(self.base_path, 'data','maps', 'world.tmx'))
         for opj in map.get_layer_by_name('Collisions'):
               collision_surface = pygame.Surface((opj.width, opj.height))
               collision_surface.fill('red')
               CollisionSprite((opj.x, opj.y), collision_surface, self.collision_sprites)
               
         for x , y , img in map.get_layer_by_name('Ground').tiles():
             Sprite((x * TILE_SIZE, y * TILE_SIZE), img, self.all_sprites)
         
         for opj in map.get_layer_by_name('Objects'):
             CollisionSprite((opj.x, opj.y), opj.image, (self.all_sprites, self.collision_sprites))
             
         for obj in map.get_layer_by_name("Entities"):
             if obj.name == "Player":
                 self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.base_path)
                 self.gun = Gun(self.player, self.all_sprites, self.base_path)
            
             else:
                 self.enemy_position.append((obj.x, obj.y))
         
         self.setup_intro_npcs()
    
    def setup_intro_npcs(self):
        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery
        
        survival_dialogue = [
            "*Greetings, warrior!*",
            "I am the Combat Instructor. I specialize in battle training.",
            "In survival mode, you'll face endless waves of enemies.",
            "Use your weapon skills and survive as long as possible!",
            "*Ready for battle?* Would you like to start combat training?"
        ]
        
        survival_npc = NPC(
            pos=(player_x - 80, player_y),
            name="Combat Instructor",
            dialogue=survival_dialogue,
            npc_type="bee",
            groups=(self.all_sprites, self.npc_sprites),
            game=self
        )
        
        guide_dialogue = [
            "*Hello, traveler!*",
            "I am the Story Guide. I've witnessed many journeys.",
            "I've seen the power of choice in the face of conflict.",
            "In story mode, you can choose to ATTACK or SPARE.",
            "*Wisdom gained* Sometimes understanding is stronger than force.",
            "Would you like me to guide you through a meaningful adventure?"
        ]
        
        guide_npc = NPC(
            pos=(player_x, player_y + 80),
            name="Story Guide", 
            dialogue=guide_dialogue,
            npc_type="dog",
            groups=(self.all_sprites, self.npc_sprites),
            game=self
        )
        
        print(f"Player spawned at: ({player_x}, {player_y})")
        print(f"NPCs placed at: Combat Instructor({player_x - 80}, {player_y}), Story Guide({player_x}, {player_y + 80})")

    def check_npc_interaction(self):
        if self.game_mode == "INTRO" and not self.npc_dialogue.active:
            player_rect = self.player.rect
            for npc in self.npc_sprites:
                if npc.get_interaction_rect().colliderect(player_rect):
                    return npc
        return None

    def gun_timer(self):
        if not self.can_shoot:
            if pygame.time.get_ticks() - self.gun_time >= self.gun_cd:
                self.can_shoot = True

    def player_collision(self):
        if self.game_mode == "EXPLORATION" and self.story_mode:
            collided_enemies = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collided_enemies:
                self.start_undertale_battle(collided_enemies[0])
        elif self.game_mode == "UNDERTALE_BATTLE":
            if self.soul:
                soul_rect = self.soul.get_rect()
                for bullet in self.undertale_bullets[:]:
                    if bullet.alive and bullet.get_rect().colliderect(soul_rect):
                        should_damage = True
                        
                        if bullet.bullet_type == 'blue':
                            keys = pygame.key.get_pressed()
                            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or 
                                   keys[pygame.K_UP] or keys[pygame.K_DOWN] or
                                   keys[pygame.K_a] or keys[pygame.K_d] or 
                                   keys[pygame.K_w] or keys[pygame.K_s]):
                                should_damage = False
                        elif bullet.bullet_type == 'orange':
                            keys = pygame.key.get_pressed()
                            if (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or 
                                keys[pygame.K_UP] or keys[pygame.K_DOWN] or
                                keys[pygame.K_a] or keys[pygame.K_d] or 
                                keys[pygame.K_w] or keys[pygame.K_s]):
                                should_damage = False
                        
                        if should_damage and self.soul.take_damage():
                            self.player_hp -= 1
                            self.freeze_timer.activate()  # Activate freeze effect
                            if self.player_hp <= 0:
                                self.pending_game_over = True  # Mark for game over after freeze
                                self.undertale_defeat = True
                                self.game_mode = "EXPLORATION"
                        bullet.alive = False
            
    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprite = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprite:
                    if self.impact_sound:
                        self.impact_sound.play()
                    for enemy in collision_sprite:
                        enemy.destroy()
                        self.score += 1
                        
                        if self.story_mode and self.game_mode == "EXPLORATION":
                            self.story_enemies_killed += 1
                            
                            if self.story_enemies_killed >= self.max_story_enemies and not self.story_message_shown:
                                self.show_story_completion_message()
                        
                        if self.score >= 400:
                            self.game_over = True
                            self.victory = True
                    bullet.kill()
    
    def show_story_completion_message(self):
        self.story_message_shown = True
        self.game_over = True
        self.victory = True
        self.story_complete = True
    
    def start_undertale_battle(self, enemy_sprite):
        self.game_mode = "UNDERTALE_BATTLE"
        self.soul = UndertaleSoul(self.battle_box.center)
        
        enemy_names = ["Skeleton", "Bat", "Blob", "Spider"]
        enemy_name = choice(enemy_names)
        self.current_undertale_enemy = UndertaleEnemy(
            name=enemy_name,
            hp=randint(20, 50),
            attacks=ATTACK_PATTERNS
        )
        
        enemy_sprite.kill()
        
        self.battle_phase = "MENU"
        self.menu_selection = 0
        self.dialogue_text = f"* {enemy_name} blocks the way!"
        self.dialogue_timer = 2000
    
    def handle_undertale_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.battle_phase == "MENU":
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.execute_menu_action()
            elif self.battle_phase == "DIALOGUE":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.start_enemy_attack()
    
    def execute_menu_action(self):
        action = self.menu_options[self.menu_selection]
        
        if action == "ATTACK":
            damage = randint(5, 15)
            if self.current_undertale_enemy.take_damage(damage):
                self.end_battle(victory=True)
                return
            self.dialogue_text = f"* You dealt {damage} damage!"
            self.battle_phase = "DIALOGUE"
            self.dialogue_timer = 2000
            
        elif action == "TALK":
            self.current_undertale_enemy.add_mercy(25)
            self.dialogue_text = f"* You talked to {self.current_undertale_enemy.name}."
            self.battle_phase = "DIALOGUE"
            self.dialogue_timer = 2000
            
        elif action == "HEAL":
            if self.player_hp < self.player_max_hp:
                self.player_hp = min(self.player_max_hp, self.player_hp + 5)
                self.dialogue_text = "* You used a healing item!"
            else:
                self.dialogue_text = "* Your HP is already full!"
            self.battle_phase = "DIALOGUE"
            self.dialogue_timer = 2000
            
        elif action == "SPARE":
            if self.current_undertale_enemy.can_spare:
                self.end_battle(victory=True, spared=True)
                return
            else:
                self.dialogue_text = f"* {self.current_undertale_enemy.name} is not ready to be spared."
                self.battle_phase = "DIALOGUE"
                self.dialogue_timer = 2000
    
    def start_enemy_attack(self):
        self.battle_phase = "DEFENDING"
        self.attack_timer = pygame.time.get_ticks()
        self.undertale_bullets = []
        
        attack_pattern = choice(self.current_undertale_enemy.attacks)
        attack_pattern(self.battle_box, self.undertale_bullets)
    
    def update_undertale_battle(self, dt):
        if self.battle_phase == "DIALOGUE":
            self.dialogue_timer -= dt * 1000
            if self.dialogue_timer <= 0:
                self.start_enemy_attack()
        
        elif self.battle_phase == "DEFENDING":
            if self.soul:
                self.soul.update(dt, self.battle_box)
            
            for bullet in self.undertale_bullets[:]:
                bullet.update(dt, self.battle_box)
                if not bullet.alive:
                    self.undertale_bullets.remove(bullet)
                    
                elif self.soul and bullet.get_rect().colliderect(self.soul.get_rect()):
                    if self.soul.take_damage():
                        self.player_hp -= 1
                        self.freeze_timer.activate()  # Activate freeze effect
                        if self.player_hp <= 0:
                            self.pending_game_over = True  # Mark for game over after freeze
                            return
            
            if pygame.time.get_ticks() - self.attack_timer > self.attack_duration:
                self.battle_phase = "MENU"
                self.undertale_bullets.clear()
                self.dialogue_text = self.current_undertale_enemy.get_dialogue()
    
    def end_battle(self, victory=True, spared=False):
        if victory:
            self.game_mode = "EXPLORATION"
            if spared:
                self.score += 5
                self.dialogue_text = "* You showed mercy!"
            else:
                self.score += 3
                self.dialogue_text = "* Victory!"
            pygame.time.wait(1000)
        else:
            self.player_hp = 0
            self.game_over = True
            self.undertale_defeat = True
            self.game_mode = "EXPLORATION"
        
        self.soul = None
        self.undertale_bullets = []
        self.current_undertale_enemy = None
        self.battle_phase = "MENU"
    
    def draw_undertale_battle(self):
        self.screen.fill((0, 0, 0))
        
        pygame.draw.rect(self.screen, (255, 255, 255), self.battle_box, 3)
        
        if self.soul and self.battle_phase == "DEFENDING":
            self.soul.draw(self.screen)
        
        for bullet in self.undertale_bullets:
            bullet.draw(self.screen)
        
        if self.current_undertale_enemy:
            name_text = self.font.render(self.current_undertale_enemy.name, True, (255, 255, 255))
            self.screen.blit(name_text, (50, 50))
            
            hp_percent = self.current_undertale_enemy.hp / self.current_undertale_enemy.max_hp
            hp_bar_width = 200
            hp_bar_height = 20
            
            pygame.draw.rect(self.screen, (255, 0, 0), (50, 80, hp_bar_width, hp_bar_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (50, 80, hp_bar_width * hp_percent, hp_bar_height))
            pygame.draw.rect(self.screen, (255, 255, 255), (50, 80, hp_bar_width, hp_bar_height), 2)
        
        hp_text = self.font.render(f"HP: {self.player_hp}/{self.player_max_hp}", True, (255, 255, 255))
        hp_text_width = hp_text.get_width()
        self.screen.blit(hp_text, (WINDOW_WIDTH - hp_text_width - 20, 50))
        
        if self.battle_phase == "MENU":
            menu_y = WINDOW_HEIGHT - 160
            menu_box = pygame.Rect(50, menu_y - 30, WINDOW_WIDTH - 100, 140)
            pygame.draw.rect(self.screen, (0, 0, 0), menu_box)
            pygame.draw.rect(self.screen, (255, 255, 255), menu_box, 3)
            
            positions = [(80, menu_y), (320, menu_y), (80, menu_y + 50), (320, menu_y + 50)]
            for i, option in enumerate(self.menu_options):
                if i < len(positions):
                    color = (255, 255, 0) if i == self.menu_selection else (255, 255, 255)
                    prefix = "★ " if i == self.menu_selection else "  "
                    option_text = self.font.render(f"{prefix}{option}", True, color)
                    self.screen.blit(option_text, positions[i])
        
        elif self.battle_phase in ["DIALOGUE", "DEFENDING"]:
            dialogue_box = pygame.Rect(50, WINDOW_HEIGHT - 100, WINDOW_WIDTH - 100, 80)
            pygame.draw.rect(self.screen, (0, 0, 0), dialogue_box)
            pygame.draw.rect(self.screen, (255, 255, 255), dialogue_box, 3)
            
            if self.dialogue_text:
                dialogue_surface = self.font.render(self.dialogue_text, True, (255, 255, 255))
                self.screen.blit(dialogue_surface, (dialogue_box.x + 10, dialogue_box.y + 10))
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            
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
                    elif self.game_mode == "INTRO":
                        if event.key == pygame.K_SPACE:
                            if self.npc_dialogue.active:
                                self.npc_dialogue.next_line()
                            else:
                                nearby_npc = self.check_npc_interaction()
                                if nearby_npc:
                                    self.npc_dialogue.start_dialogue(nearby_npc)
                    elif self.game_mode == "UNDERTALE_BATTLE":
                        self.handle_undertale_input(event)
                        
                if event.type == self.enemy_event and not self.game_over and self.game_mode in ["EXPLORATION", "SURVIVAL_ONLY"]:
                    if self.story_mode and self.story_enemies_spawned >= self.max_story_enemies:
                        pass
                    else:
                        stationary = self.story_mode
                        enemy = Enemy(choice(self.enemy_position), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, stationary)
                        if self.story_mode:
                            self.story_enemies_spawned += 1

            if not self.game_over:
                # Update freeze timer
                self.freeze_timer.update()
                
                # Check if game over should happen after freeze ends
                if self.pending_game_over and not self.freeze_timer:
                    self.game_over = True
                    self.pending_game_over = False
                
                if self.game_mode == "INTRO":
                    # Only update if not frozen
                    if not self.freeze_timer:
                        self.all_sprites.update(dt)
                        for npc in self.npc_sprites:
                            npc.update(dt)
                elif self.game_mode in ["EXPLORATION", "SURVIVAL_ONLY"]:
                    self.gun_timer()
                    # Only update game logic if not frozen
                    if not self.freeze_timer:
                        self.input()
                        self.all_sprites.update(dt)
                        self.bullet_collision()
                        if self.story_mode and self.game_mode == "EXPLORATION":
                            self.player_collision()
                        else:
                            if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
                                self.freeze_timer.activate()  # Activate freeze on collision
                                self.pending_game_over = True  # Mark for game over after freeze
                elif self.game_mode == "UNDERTALE_BATTLE":
                    # Only update battle if not frozen
                    if not self.freeze_timer:
                        self.update_undertale_battle(dt)
                        self.player_collision()
            
            if self.game_mode in ["INTRO", "EXPLORATION", "SURVIVAL_ONLY"]:
                self.screen.fill(('black'))
                
                if not self.game_over:
                    self.all_sprites.draw(self.player.rect.center)
                    score_text = self.font.render(f"Score: {self.score}", True, "white")
                    self.screen.blit(score_text, (10, 10))
                    
                    hp_text = self.font.render(f"HP: {self.player_hp}/{self.player_max_hp}", True, "red")
                    self.screen.blit(hp_text, (10, 50))
                    
                    if self.game_mode == "INTRO":
                        intro_title = self.title_font.render("Choose Your Adventure!", True, (16, 233, 160))
                        title_rect = intro_title.get_rect(center=(WINDOW_WIDTH//2, 50))
                        self.screen.blit(intro_title, title_rect)

                        instructions = self.font.render("Walk up to an NPC and press SPACE to talk", True, (180, 18, 180))  
                        inst_rect = instructions.get_rect(center=(WINDOW_WIDTH//2, 100))
                        self.screen.blit(instructions, inst_rect)

                        direction_text_lines = [
                            "Look left for Combat Instructor,",
                            "below for Story Guide"
                        ]
                        for i, line in enumerate(direction_text_lines):
                            direction_text = self.font.render(line, True, (180, 18, 180)) 
                            dir_rect = direction_text.get_rect(center=(WINDOW_WIDTH//2, 130 + i * 30))
                            self.screen.blit(direction_text, dir_rect)

                        nearby_npc = self.check_npc_interaction()
                        if nearby_npc and not self.npc_dialogue.active:
                            hint_text = self.font.render(f"Press SPACE to talk to {nearby_npc.name}", True, (144, 238, 144))  # Light green for encouragement
                            hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 150))
                            self.screen.blit(hint_text, hint_rect)
                    
                    self.npc_dialogue.draw(self.screen)
                else:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    overlay.set_alpha(200)
                    overlay.fill((0, 0, 0))
                    self.screen.blit(overlay, (0, 0))
                    
                    if hasattr(self, 'story_complete') and self.story_complete:
                        game_over_text = self.game_over_font.render("REFLECTION", True, (255, 215, 0))
                        
                        deep_messages = [
                            "Sometimes the greatest victory",
                            "is choosing not to fight at all.",
                            "",
                            "In a world full of conflict,",
                            "compassion becomes the rarest weapon.",
                            "",
                            "You faced your fears,",
                            "and found understanding instead."
                        ]
                        
                        for i, line in enumerate(deep_messages):
                            if line:
                                color = (255, 215, 0) if i < 2 else (200, 200, 255)
                                message_text = self.font.render(line, True, color)
                                message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60 + i * 35))
                                self.screen.blit(message_text, message_rect)
                                
                    elif hasattr(self, 'victory') and self.victory:
                        game_over_text = self.game_over_font.render("VICTORY!", True, (100, 255, 100))
                        victory_subtitle = self.title_font.render("Quest Complete!", True, (200, 255, 200))
                        subtitle_rect = victory_subtitle.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60))
                        self.screen.blit(victory_subtitle, subtitle_rect)
                    else:
                        if hasattr(self, 'undertale_defeat') and self.undertale_defeat:
                            game_over_text = self.game_over_font.render("DETERMINATION FAILED", True, (255, 50, 50))
                            
                            defeat_msg = self.title_font.render("You ran out of HP!", True, (255, 100, 100))
                            defeat_rect = defeat_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60))
                            self.screen.blit(defeat_msg, defeat_rect)
                            
                            battle_msg = self.font.render("The enemy's attacks proved too much...", True, (200, 150, 150))
                            battle_rect = battle_msg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
                            self.screen.blit(battle_msg, battle_rect)
                        else:
                            game_over_text = self.game_over_font.render("GAME OVER", True, (255, 50, 50))
                    game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 150))
                    self.screen.blit(game_over_text, game_over_rect)
                    
                    if not (hasattr(self, 'story_complete') and self.story_complete):
                        final_score_text = self.title_font.render(f"Final Score: {self.score}", True, "white")
                        score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))
                        self.screen.blit(final_score_text, score_rect)
                    
                    if hasattr(self, 'story_complete') and self.story_complete:
                        restart_text = self.font.render("Press ESC to return to menu", True, (200, 200, 200))
                        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 260))
                        self.screen.blit(restart_text, restart_rect)
                        
                        quit_text = self.font.render("Press Q to quit", True, (200, 200, 200))
                        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 300))
                        self.screen.blit(quit_text, quit_rect)
                    else:
                        restart_text = self.font.render("Press ESC to return to menu", True, (200, 200, 200))
                        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 140))
                        self.screen.blit(restart_text, restart_rect)
                        
                        quit_text = self.font.render("Press Q to quit", True, (200, 200, 200))
                        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 180))
                        self.screen.blit(quit_text, quit_rect)
                    
            elif self.game_mode == "UNDERTALE_BATTLE":
                self.draw_undertale_battle()
            
            # Add freeze effect overlay
            if self.freeze_timer:
                freeze_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                freeze_overlay.set_alpha(30)
                freeze_overlay.fill((150, 200, 255))  # Light blue freeze effect
                self.screen.blit(freeze_overlay, (0, 0))
            
            pygame.display.update()

        pygame.quit()
        
if __name__ == "__main__":
    game = Game()
    game.run()