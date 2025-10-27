from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from group import AllSprites
from random import randint, choice
from undertale_mechanics import *
from npc_system import *
from timer import Timer
import pygame_gui
import sys
import os
import math

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
        
        # Boundary constraints for player and camera
        self.boundary_rect = None
        
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
        self.player_max_hp = 50
        
        self.npc_sprites = pygame.sprite.Group()
        self.npc_dialogue = NPCDialogue(self)
        self.intro_complete = False
        
        self.can_shoot = True
        self.gun_cd = 100
        self.shoot_time = 0
        
        # Damage system for enemy collisions
        self.damage_cooldown = False
        self.damage_cd_time = 1000  # 1 second invincibility after taking damage
        self.last_damage_time = 0
        
        # THEME MECHANICS: Invisibility (IMPROVED)
        self.player_invisible = False
        self.last_move_time = 0
        self.invisibility_delay = 1500  # 1.5 seconds to become invisible (faster)
        self.invisibility_alpha = 0  # Smooth fade effect
        
        # THEME MECHANICS: Memory Overload - Enemy Ghost Positions (IMPROVED)
        self.enemy_ghosts = []  # List of dicts with pos, timestamp, size, enemy_type
        self.ghost_duration = 5000  # 5 seconds (longer to track better)
        self.ghost_update_timer = 0
        self.ghost_update_interval = 500  # Update ghosts every 0.5s
        
        # THEME MECHANICS: Memory Overload - Fading Mini-Map (IMPROVED)
        self.visited_tiles = {}  # {(x, y): timestamp}
        self.tile_memory_duration = 20000  # 20 seconds (longer memory)
        self.minimap_scale = 3  # Smaller pixels for more detail
        self.minimap_size = 250  # Bigger minimap
        
        # THEME MECHANICS: Blinking Enemies (IMPROVED)
        self.enemy_blink_timer = 0
        self.enemy_visible = True
        self.blink_interval = 1500  # 1.5 seconds (faster blinks, more challenging)
        self.blink_duration = 400  # How long they stay invisible
        
        self.coins = 0  # Currency for buying items
        self.victory = False
        
        # Shop system
        self.shop_open = False
        self.shop_items = [
            {"name": "Health Pack", "price": 5, "description": "Restore 2 HP"},
            {"name": "Max HP Upgrade", "price": 10, "description": "+5 Max HP"},
            {"name": "Speed Boost", "price": 8, "description": "+50 Movement Speed"},
            {"name": "Damage Boost", "price": 12, "description": "Bullets deal more damage"}
        ]
        self.shop_selection = 0
        self.nearby_shop = None
        
        # pygame_gui Manager for modern UI
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Register custom pixel font with pygame_gui
        font_path = os.path.join(self.base_path, '..', 'fonts', '04B_30__.TTF')
        if os.path.exists(font_path):
            try:
                # Pre-load the font at various sizes for pygame_gui
                pygame_gui.core.utility.create_resource_path(font_path)
            except Exception as e:
                print(f"Could not register font with pygame_gui: {e}")
        
        # Load custom theme if available
        theme_path = os.path.join(self.base_path, 'shop_theme.json')
        if os.path.exists(theme_path):
            try:
                self.ui_manager.get_theme().load_theme(theme_path)
            except Exception as e:
                print(f"Could not load shop theme: {e}")
        
        self.shop_window = None
        self.shop_buttons = []
        
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
        
        # Flashlight / visibility settings
        self.flashlight_enabled = True
        # Extend beam across the whole screen (diagonal)
        import math
        self.flashlight_length = int(math.hypot(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.flashlight_angle_deg = 60  # full cone angle
        self.night_alpha = 200  # 0-255 darkness outside cone
        # Start the beam a bit in front of the player to avoid a pointy apex at the origin
        self.flashlight_start_offset = 36  # px ahead of player along aim direction
        
        self.enemy_event = pygame.event.custom_type()
        self.enemy_spawn_rate = 1200  # Start slower (was 300)
        pygame.time.set_timer(self.enemy_event, self.enemy_spawn_rate)
        self.last_spawn_update = 0
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

    def _vector_angle_deg(self, a, b):
        """Return angle in degrees between 2 vectors a and b (both pygame.Vector2)."""
        if a.length_squared() == 0 or b.length_squared() == 0:
            return 180
        cosang = max(-1.0, min(1.0, a.normalize().dot(b.normalize())))
        import math
        return math.degrees(math.acos(cosang))

    def enemy_in_flashlight(self, enemy_pos):
        """Check if an enemy (world coords) is within the flashlight cone from the player."""
        if not self.flashlight_enabled or not hasattr(self, 'gun'):
            return False
        player_pos = pygame.Vector2(self.player.rect.center)
        to_enemy = pygame.Vector2(enemy_pos) - player_pos
        dist = to_enemy.length()
        # Ignore targets closer than the start offset to match the visual gap
        if dist < getattr(self, 'flashlight_start_offset', 0):
            return False
        if dist > self.flashlight_length:
            return False
        # Use gun direction
        dir_vec = pygame.Vector2(getattr(self.gun, 'player_dir', (1, 0)))
        ang = self._vector_angle_deg(dir_vec, to_enemy)
        return ang <= (self.flashlight_angle_deg / 2)

    def draw_flashlight_overlay(self):
        """Darken the screen with a soft, realistic flashlight beam that starts a bit ahead of the player.

        Implements a rounded beam with inner cutoff (no triangle apex at the player) and smooth falloff.
        """
        if not self.flashlight_enabled or not hasattr(self, 'gun'):
            return
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.night_alpha))  # base darkness

        # Calculate player's screen position based on camera offset
        player_world_pos = self.player.rect.center
        camera_offset = self.all_sprites.offset
        origin = pygame.Vector2(
            player_world_pos[0] + camera_offset.x,
            player_world_pos[1] + camera_offset.y
        )
        
        dir_vec = pygame.Vector2(getattr(self.gun, 'player_dir', (1, 0)))
        if dir_vec.length_squared() == 0:
            dir_vec = pygame.Vector2(1, 0)

        import math
        half_angle_rad = math.radians(self.flashlight_angle_deg / 2)

        # Place the beam emitter slightly ahead of the player to avoid a pointy look at the origin
        emitter = origin + dir_vec * getattr(self, 'flashlight_start_offset', 0)

        def ring_points(inner_r, outer_r, angle_scale=1.0, steps=28):
            """Return points approximating an annular sector (ring slice) centered at emitter."""
            pts = []
            start = -half_angle_rad * angle_scale
            end = half_angle_rad * angle_scale
            # Outer arc from left to right
            for i in range(steps + 1):
                t = start + (end - start) * (i / steps)
                ct = math.cos(t)
                st = math.sin(t)
                rx = dir_vec.x * ct - dir_vec.y * st
                ry = dir_vec.x * st + dir_vec.y * ct
                pts.append(emitter + pygame.Vector2(rx, ry) * outer_r)
            # Inner arc from right back to left
            for i in range(steps, -1, -1):
                t = start + (end - start) * (i / steps)
                ct = math.cos(t)
                st = math.sin(t)
                rx = dir_vec.x * ct - dir_vec.y * st
                ry = dir_vec.x * st + dir_vec.y * ct
                pts.append(emitter + pygame.Vector2(rx, ry) * inner_r)
            return pts

        # Draw gradient falloff from outside to inside using multiple sectors
        # Each layer overwrites alpha with a lower value, producing a smooth transition
        # Each layer: (inner_scale, outer_scale, alpha, angle_scale)
        so = getattr(self, 'flashlight_start_offset', 0)
        L = self.flashlight_length
        clamp = lambda v: max(0, min(255, int(v)))
        layers = [
            (so, L * 0.95, clamp(self.night_alpha - 60), 1.00),
            (so, L * 0.85, clamp(self.night_alpha - 110), 0.98),
            (so, L * 0.72, clamp(self.night_alpha - 150), 0.95),
            (so, L * 0.58, clamp(self.night_alpha - 180), 0.92),
            (so, L * 0.45, 40, 0.90),
            (so, L * 0.33, 15, 0.88),
            (so, L * 0.22, 0, 0.85),  # inner core fully clear, begins at the offset
        ]

        for inner_r, outer_r, alpha, a_scale in layers:
            pts = ring_points(inner_r, outer_r, angle_scale=a_scale, steps=28)
            pygame.draw.polygon(overlay, (0, 0, 0, alpha), pts)

        # Warm light tint inside cone for a more realistic torch hue
        light_tint = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        tint_pts = ring_points(so, L * 0.5, angle_scale=0.92, steps=28)
        pygame.draw.polygon(light_tint, (255, 240, 180, 28), tint_pts)

        # Small glow around player for ambient spill
        glow = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 200, 36), origin + dir_vec * (so * 0.4), 70)

        # Composite
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(light_tint, (0, 0))
        self.screen.blit(glow, (0, 0))
    
    def draw_enemy_ghosts(self):
        """THEME: Memory Overload - Draw enhanced fading ghosts showing last known enemy positions."""
        current_time = pygame.time.get_ticks()
        
        for ghost in self.enemy_ghosts:
            age = current_time - ghost['timestamp']
            alpha = int(200 * (1 - age / self.ghost_duration))  # Fade from 200 to 0
            
            if alpha <= 0:
                continue
            
            # Convert world position to screen position
            screen_pos = (
                ghost['pos'][0] - self.player.rect.centerx + WINDOW_WIDTH // 2,
                ghost['pos'][1] - self.player.rect.centery + WINDOW_HEIGHT // 2
            )
            
            # Draw pulsing circle effect
            pulse_scale = 1.0 + 0.3 * (age / self.ghost_duration)  # Grow as they fade
            radius = int(ghost['size'][0] // 2 * pulse_scale)
            
            # Outer glow
            for i in range(3, 0, -1):
                glow_alpha = alpha // (i + 1)
                glow_surface = pygame.Surface((radius * 2 + i * 10, radius * 2 + i * 10), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 50, 50, glow_alpha), 
                                 (radius + i * 5, radius + i * 5), radius + i * 3)
                self.screen.blit(glow_surface, (screen_pos[0] - radius - i * 5, 
                                                screen_pos[1] - radius - i * 5))
            
            # Core ghost with X marker
            ghost_surface = pygame.Surface(ghost['size'], pygame.SRCALPHA)
            ghost_color = (255, 100, 100, alpha)
            pygame.draw.ellipse(ghost_surface, ghost_color, ghost_surface.get_rect(), 3)
            
            # Add X marker to show "last seen here"
            x_size = ghost['size'][0] // 3
            pygame.draw.line(ghost_surface, (255, 150, 150, alpha), 
                           (ghost['size'][0]//2 - x_size, ghost['size'][1]//2 - x_size),
                           (ghost['size'][0]//2 + x_size, ghost['size'][1]//2 + x_size), 2)
            pygame.draw.line(ghost_surface, (255, 150, 150, alpha),
                           (ghost['size'][0]//2 + x_size, ghost['size'][1]//2 - x_size),
                           (ghost['size'][0]//2 - x_size, ghost['size'][1]//2 + x_size), 2)
            
            self.screen.blit(ghost_surface, (screen_pos[0] - ghost['size'][0]//2, 
                                            screen_pos[1] - ghost['size'][1]//2))
    
    def draw_blinking_enemies(self):
        """THEME: Invisibility - Enemies completely disappear during blink phase.
        
        Note: The actual disappearing is handled in group.py by skipping enemy rendering.
        This function can be used for additional effects if needed.
        """
        # Enemies are now made invisible in group.py by not drawing them
        # You could add a subtle "enemies are blinking" indicator here if desired
        pass
    
    def draw_player_invisible(self):
        """THEME: Invisibility - Enhanced visual feedback when player is invisible or charging."""
        # Calculate actual player screen position with camera offset
        camera_offset = self.all_sprites.offset
        player_screen_x = self.player.rect.centerx + camera_offset.x
        player_screen_y = self.player.rect.centery + camera_offset.y
        player_screen_pos = (player_screen_x, player_screen_y)
        
        if self.invisibility_alpha > 0:
            # Pulsing glow effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            alpha = int(min(self.invisibility_alpha, 180) * (0.7 + 0.3 * pulse))
            
            # Multiple rings for better effect
            for i in range(3):
                ring_size = (self.player.rect.width + i * 20, self.player.rect.height + i * 20)
                ring_alpha = alpha // (i + 1)
                
                ring_surf = pygame.Surface(ring_size, pygame.SRCALPHA)
                
                if self.player_invisible:
                    # Fully invisible - blue/cyan glow
                    pygame.draw.ellipse(ring_surf, (100, 200, 255, ring_alpha), ring_surf.get_rect(), 3)
                else:
                    # Charging invisibility - yellow glow
                    pygame.draw.ellipse(ring_surf, (255, 255, 100, ring_alpha), ring_surf.get_rect(), 2)
                
                self.screen.blit(ring_surf, (player_screen_pos[0] - ring_size[0]//2, 
                                            player_screen_pos[1] - ring_size[1]//2))
        
        if self.player_invisible:
            # Big text indicator with shadow
            text_color = (100, 220, 255)
            shadow_color = (20, 50, 80)
            
            invisible_text = self.font.render("INVISIBLE", True, text_color)
            text_rect = invisible_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 80))
            
            # Shadow
            shadow_text = self.font.render("INVISIBLE", True, shadow_color)
            self.screen.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
            # Main text
            self.screen.blit(invisible_text, text_rect)
            
            # Progress bar showing how long you've been invisible
            bar_width = 200
            bar_height = 10
            bar_x = WINDOW_WIDTH // 2 - bar_width // 2
            bar_y = WINDOW_HEIGHT - 60
            
            pygame.draw.rect(self.screen, (50, 50, 80), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (100, 220, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        else:
            # Show charging progress
            time_still = pygame.time.get_ticks() - self.last_move_time
            if time_still > 0 and time_still < self.invisibility_delay:
                progress = time_still / self.invisibility_delay
                
                bar_width = 200
                bar_height = 10
                bar_x = WINDOW_WIDTH // 2 - bar_width // 2
                bar_y = WINDOW_HEIGHT - 80
                
                # Background
                pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                # Progress
                pygame.draw.rect(self.screen, (255, 255, 100), (bar_x, bar_y, int(bar_width * progress), bar_height))
                # Border
                pygame.draw.rect(self.screen, (200, 200, 100), (bar_x, bar_y, bar_width, bar_height), 2)
                
                # Text
                charging_text = self.font.render("Becoming Invisible...", True, (255, 255, 150))
                text_rect = charging_text.get_rect(center=(WINDOW_WIDTH//2, bar_y - 15))
                self.screen.blit(charging_text, text_rect)
    
    def draw_minimap(self):
        """THEME: Memory Overload - Enhanced fading minimap showing memory decay."""
        minimap_x = WINDOW_WIDTH - self.minimap_size - 20
        minimap_y = 20
        
        # Fancy background with gradient
        minimap_bg = pygame.Surface((self.minimap_size, self.minimap_size), pygame.SRCALPHA)
        minimap_bg.fill((10, 10, 20, 200))
        
        # Inner darker region
        inner_rect = pygame.Rect(5, 5, self.minimap_size-10, self.minimap_size-10)
        pygame.draw.rect(minimap_bg, (5, 5, 10, 220), inner_rect)
        
        # Border with glow
        pygame.draw.rect(minimap_bg, (100, 150, 200), minimap_bg.get_rect(), 3)
        pygame.draw.rect(minimap_bg, (60, 100, 150), minimap_bg.get_rect(), 1)
        
        self.screen.blit(minimap_bg, (minimap_x, minimap_y))
        
        # Title
        title_font = getattr(self, 'minimap_title_font', self.font)
        title_text = title_font.render("memory", True, (100, 180, 255))
        title_rect = title_text.get_rect(center=(minimap_x + self.minimap_size // 2, minimap_y - 15))
        self.screen.blit(title_text, title_rect)
        
        # Draw visited tiles
        current_time = pygame.time.get_ticks()
        
        if hasattr(self, 'player'):
            player_tile_x = int(self.player.rect.centerx // TILE_SIZE)
            player_tile_y = int(self.player.rect.centery // TILE_SIZE)
            
            tiles_drawn = 0
            for (tile_x, tile_y), timestamp in self.visited_tiles.items():
                # Calculate age and alpha
                age = current_time - timestamp
                alpha = int(255 * (1 - age / self.tile_memory_duration))
                
                if alpha <= 0:
                    continue
                
                # Position relative to player
                rel_x = (tile_x - player_tile_x) * self.minimap_scale + self.minimap_size // 2
                rel_y = (tile_y - player_tile_y) * self.minimap_scale + self.minimap_size // 2
                
                # Only draw if within minimap bounds
                if 5 <= rel_x < self.minimap_size - 5 and 5 <= rel_y < self.minimap_size - 5:
                    tiles_drawn += 1
                    
                    # Color changes from bright green (new) to dim cyan (old)
                    age_ratio = age / self.tile_memory_duration
                    r = int(0 * (1 - age_ratio) + 50 * age_ratio)
                    g = int(255 * (1 - age_ratio) + 180 * age_ratio)
                    b = int(100 * (1 - age_ratio) + 200 * age_ratio)
                    
                    tile_surf = pygame.Surface((self.minimap_scale, self.minimap_scale), pygame.SRCALPHA)
                    tile_surf.fill((r, g, b, alpha))
                    self.screen.blit(tile_surf, (minimap_x + int(rel_x), minimap_y + int(rel_y)))
            
            # Draw enemies on minimap (ONLY in non-faded discovered areas OR under flashlight)
            for enemy in self.enemy_sprites:
                if enemy.death_time == 0:  # Only living enemies
                    enemy_tile_x = int(enemy.rect.centerx // TILE_SIZE)
                    enemy_tile_y = int(enemy.rect.centery // TILE_SIZE)
                    
                    # Check if enemy is in flashlight
                    in_flashlight = getattr(enemy, 'frozen_by_light', False)
                    
                    # Check if enemy is in a NON-FADED discovered area
                    is_discovered_and_visible = False
                    for dx in range(-1, 2):  # Check 3x3 area around enemy
                        for dy in range(-1, 2):
                            tile_key = (enemy_tile_x + dx, enemy_tile_y + dy)
                            if tile_key in self.visited_tiles:
                                # Check if this tile hasn't faded yet
                                age = current_time - self.visited_tiles[tile_key]
                                if age < self.tile_memory_duration:  # Tile is still visible
                                    is_discovered_and_visible = True
                                    break
                        if is_discovered_and_visible:
                            break
                    
                    # Show enemy ONLY if in non-faded discovered area OR currently in flashlight
                    if is_discovered_and_visible or in_flashlight:
                        # Calculate enemy position on minimap
                        enemy_rel_x = (enemy_tile_x - player_tile_x) * self.minimap_scale + self.minimap_size // 2
                        enemy_rel_y = (enemy_tile_y - player_tile_y) * self.minimap_scale + self.minimap_size // 2
                        
                        # Draw if within minimap bounds
                        if 5 <= enemy_rel_x < self.minimap_size - 5 and 5 <= enemy_rel_y < self.minimap_size - 5:
                            # Different colors: bright red for flashlight, normal red for discovered
                            if in_flashlight:
                                # Brighter pulsing for enemies in flashlight
                                pulse = abs(math.sin(pygame.time.get_ticks() * 0.012))
                                enemy_alpha = 255
                                color = (255, 255, 100)  # Yellow for enemies in light
                            else:
                                # Normal red for discovered enemies
                                pulse = abs(math.sin(pygame.time.get_ticks() * 0.008))
                                enemy_alpha = int(200 + 55 * pulse)
                                color = (255, 50, 50)  # Red for discovered enemies
                            
                            # Draw enemy marker with appropriate color
                            pygame.draw.circle(self.screen, (*color, enemy_alpha),
                                             (minimap_x + int(enemy_rel_x), minimap_y + int(enemy_rel_y)), 3)
                            # Outer glow
                            glow_color = (255, 255, 150) if in_flashlight else (255, 100, 100)
                            pygame.draw.circle(self.screen, (*glow_color, enemy_alpha // 2),
                                             (minimap_x + int(enemy_rel_x), minimap_y + int(enemy_rel_y)), 4, 1)
            
            # Draw player position with pulsing effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            player_size = int(4 + 2 * pulse)
            pygame.draw.circle(self.screen, (255, 255, 100), 
                             (minimap_x + self.minimap_size // 2, minimap_y + self.minimap_size // 2), player_size)
            pygame.draw.circle(self.screen, (255, 255, 0), 
                             (minimap_x + self.minimap_size // 2, minimap_y + self.minimap_size // 2), player_size, 1)
            
            # Memory stats with enemy count
            enemy_count = sum(1 for e in self.enemy_sprites if e.death_time == 0)
            color = (150, 200, 255)
            tiles_text = self.font.render(f"{tiles_drawn} tiles", True, color)
            enemies_text = self.font.render(f"{enemy_count} enemies", True, color)
            base_x = minimap_x + 5
            base_y = minimap_y + self.minimap_size + 5
            self.screen.blit(tiles_text, (base_x, base_y))
            self.screen.blit(enemies_text, (base_x, base_y + tiles_text.get_height() + 2))
    
    def update_enemy_spawn_rate(self):
        """Adjust enemy spawn rate and speed based on player's coin count (progression system)."""
        current_time = pygame.time.get_ticks()
        
        # Only update every 5 seconds to avoid constant timer resets
        if current_time - self.last_spawn_update < 5000:
            return
        
        self.last_spawn_update = current_time
        
        # Calculate spawn rate and enemy speed based on coins (more coins = faster spawns + faster enemies)
        if self.coins <= 50:
            # Early game: Very slow spawns, slow enemies
            new_rate = 1200  # 1.2 seconds per enemy
            new_speed = 200
        elif self.coins <= 100:
            # Early-mid game: Slow spawns, slower enemies
            new_rate = 900
            new_speed = 250
        elif self.coins <= 200:
            # Mid game: Medium spawns, medium enemies
            new_rate = 600
            new_speed = 300
        elif self.coins <= 300:
            # Mid-late game: Fast spawns, normal enemies
            new_rate = 400
            new_speed = 350
        else:
            # Late game: Very fast spawns, fast enemies
            new_rate = 250
            new_speed = 400
        
        # Update existing enemies' speed to match current difficulty
        for enemy in self.enemy_sprites:
            if enemy.death_time == 0:  # Only living enemies
                enemy.speed = new_speed
        
        # Only update spawn timer if rate changed significantly
        if abs(new_rate - self.enemy_spawn_rate) > 50:
            self.enemy_spawn_rate = new_rate
            pygame.time.set_timer(self.enemy_event, self.enemy_spawn_rate)
    
    def load_images(self):
        # Load and scale down bullet for better proportion
        bullet_img = pygame.image.load(os.path.join(self.base_path, 'images', 'gun', 'bullet.png')).convert_alpha()
        bullet_scale = 0.5  # 50% size
        bw, bh = bullet_img.get_size()
        new_size = (max(1, int(bw * bullet_scale)), max(1, int(bh * bullet_scale)))
        self.bullet_surface = pygame.transform.smoothscale(bullet_img, new_size)
        folders = list(walk(os.path.join(self.base_path, 'images','enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, image_names in walk(os.path.join(self.base_path, 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
                    full_path = os.path.join(folder_path, image_name)
                    surface = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surface)
    
    def check_nearby_shop(self):
        """Check if player is near the shop for interaction."""
        if hasattr(self, 'shop_sprite') and hasattr(self, 'player'):
            distance = pygame.Vector2(self.player.rect.center).distance_to(self.shop_sprite.rect.center)
            self.nearby_shop = distance < 100  # Interaction range in pixels
        else:
            self.nearby_shop = False
    
    def update_player_invisibility(self):
        """THEME: Invisibility - Player becomes invisible when standing still with smooth fade."""
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Check if player is moving or shooting
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d] or mouse_buttons[0]:
            self.last_move_time = pygame.time.get_ticks()
            self.player_invisible = False
            self.invisibility_alpha = max(0, self.invisibility_alpha - 15)  # Fast fade out
        else:
            # Player is standing still
            time_still = pygame.time.get_ticks() - self.last_move_time
            if time_still >= self.invisibility_delay:
                self.player_invisible = True
                self.invisibility_alpha = min(255, self.invisibility_alpha + 10)  # Smooth fade in
            else:
                # Show charging effect
                self.invisibility_alpha = int((time_still / self.invisibility_delay) * 100)
    
    def update_enemy_ghosts(self):
        """THEME: Memory Overload - Create better fading ghost positions of enemies outside flashlight."""
        current_time = pygame.time.get_ticks()
        
        # Only update ghosts periodically to avoid spam
        if current_time - self.ghost_update_timer < self.ghost_update_interval:
            # Still clean up old ghosts
            self.enemy_ghosts = [g for g in self.enemy_ghosts if current_time - g['timestamp'] < self.ghost_duration]
            return
        
        self.ghost_update_timer = current_time
        
        # Add new ghosts for enemies NOT in flashlight (showing where they were last seen)
        for enemy in self.enemy_sprites:
            if enemy.death_time == 0:  # Only living enemies
                in_light = getattr(enemy, 'frozen_by_light', False)
                
                # Create ghost when enemy is OUTSIDE light (last known position)
                if not in_light:
                    # Only create if we don't have a recent ghost for this position
                    should_create = True
                    for ghost in self.enemy_ghosts:
                        if pygame.Vector2(ghost['pos']).distance_to(enemy.rect.center) < 50:
                            should_create = False
                            break
                    
                    if should_create:
                        self.enemy_ghosts.append({
                            'pos': enemy.rect.center,
                            'timestamp': current_time,
                            'size': enemy.rect.size,
                            'enemy_type': getattr(enemy, 'enemy_type', 'normal')
                        })
        
        # Remove old ghosts
        self.enemy_ghosts = [g for g in self.enemy_ghosts if current_time - g['timestamp'] < self.ghost_duration]
    
    def update_minimap_memory(self):
        """THEME: Memory Overload - Track visited tiles for fading minimap."""
        current_time = pygame.time.get_ticks()
        
        # Record current player tile
        if hasattr(self, 'player'):
            tile_x = int(self.player.rect.centerx // TILE_SIZE)
            tile_y = int(self.player.rect.centery // TILE_SIZE)
            
            # Mark nearby tiles as visited (player's vision range)
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    self.visited_tiles[(tile_x + dx, tile_y + dy)] = current_time
        
        # Remove old memories
        tiles_to_remove = []
        for tile, timestamp in self.visited_tiles.items():
            if current_time - timestamp > self.tile_memory_duration:
                tiles_to_remove.append(tile)
        
        for tile in tiles_to_remove:
            del self.visited_tiles[tile]
    
    def update_enemy_blinking(self, dt):
        """THEME: Invisibility - Enemies blink in and out of visibility with proper timing."""
        self.enemy_blink_timer += dt * 1000
        
        if self.enemy_visible:
            # Enemies are visible, wait for interval
            if self.enemy_blink_timer >= self.blink_interval:
                self.enemy_visible = False
                self.enemy_blink_timer = 0
        else:
            # Enemies are invisible, show them after blink duration
            if self.enemy_blink_timer >= self.blink_duration:
                self.enemy_visible = True
                self.enemy_blink_timer = 0
    
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
         
         # Set boundary to the map dimensions (no blank space outside the tilemap)
         map_width = map.width * map.tilewidth
         map_height = map.height * map.tileheight
         self.boundary_rect = pygame.Rect(0, 0, map_width, map_height)
         print(f"Map boundary set to: {self.boundary_rect}")
         
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
                 self.player.game = self  # THEME: Link player to game for invisibility
                 self.gun = Gun(self.player, self.all_sprites, self.base_path)
                 # Set boundary constraint on player
                 self.player.boundary_rect = self.boundary_rect
             elif obj.name == "Shop":
                 # Spawn idle, animated shop (collidable at feet)
                 self.shop_sprite = Shop((obj.x, obj.y), self.all_sprites, self.base_path, collision_group=self.collision_sprites)
             else:
                 self.enemy_position.append((obj.x, obj.y))
         
         self.setup_intro_npcs()
    
    def setup_intro_npcs(self):
        # No NPCs in intro anymore; simple press-to-start flow
        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery
        print(f"Player spawned at: ({player_x}, {player_y})")
        print("Intro mode: Press ENTER to begin")
        
        # Set boundary on camera
        if self.boundary_rect:
            self.all_sprites.boundary_rect = self.boundary_rect

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
    
    def take_damage(self, amount):
        """Handle player taking damage with cooldown."""
        current_time = pygame.time.get_ticks()
        if not self.damage_cooldown:
            self.player_hp -= amount
            self.damage_cooldown = True
            self.last_damage_time = current_time
            self.freeze_timer.activate()  # Brief freeze effect when hit
            
            # Flash effect or sound could go here
            if self.player_hp <= 0:
                self.pending_game_over = True
                self.player_hp = 0
            
            print(f"Took {amount} damage! HP: {self.player_hp}/{self.player_max_hp}")
    
    def update_damage_cooldown(self):
        """Update damage cooldown timer."""
        if self.damage_cooldown:
            if pygame.time.get_ticks() - self.last_damage_time >= self.damage_cd_time:
                self.damage_cooldown = False

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
                        self.coins += 1  # Earn coins for killing enemies
                        
                        if self.story_mode and self.game_mode == "EXPLORATION":
                            self.story_enemies_killed += 1
                            
                            if self.story_enemies_killed >= self.max_story_enemies and not self.story_message_shown:
                                self.show_story_completion_message()
                        
                        if self.coins >= 400:
                            self.game_over = True
                            self.victory = True
                    bullet.kill()
    
    def open_shop_gui(self):
        """Open the pygame_gui shop window with improved design."""
        if self.shop_window is not None:
            return  # Already open
        
        self.shop_open = True
        pygame.event.set_grab(False)  # Release mouse for UI interaction
        pygame.mouse.set_visible(True)
        
        # Create larger, more spacious shop window
        window_width = 750
        window_height = 650
        window_rect = pygame.Rect(
            (WINDOW_WIDTH - window_width) // 2,
            (WINDOW_HEIGHT - window_height) // 2,
            window_width,
            window_height
        )
        
        self.shop_window = pygame_gui.elements.UIWindow(
            rect=window_rect,
            window_display_title='MERCHANT SHOP',
            manager=self.ui_manager,
            object_id='#shop_window'
        )
        
        # Title banner with pixel art aesthetic
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(15, 15, window_width - 50, 55),
            text='=== ADVENTURE SUPPLIES ===',
            manager=self.ui_manager,
            container=self.shop_window,
            object_id='#title_label'
        )
        
        # Coins display with better styling
        coins_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(25, 80, window_width - 70, 50),
            text=f'GOLD: {self.coins} COINS',
            manager=self.ui_manager,
            container=self.shop_window,
            object_id='#coins_label'
        )
        
        # Divider line effect
        divider = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(40, 135, window_width - 100, 4),
            text='',
            manager=self.ui_manager,
            container=self.shop_window,
            object_id='#divider'
        )
        
        # Create item buttons in a 2x2 grid with better spacing
        self.shop_buttons = []
        button_width = 330
        button_height = 110
        x_positions = [25, 385]
        y_positions = [155, 285, 415]
        
        for i, item in enumerate(self.shop_items):
            can_afford = self.coins >= item['price']
            
            # Position in grid
            x = x_positions[i % 2]
            y = y_positions[i // 2]
            
            # Create button with emoji icons
            emoji_map = {
                "Health Pack": "+2 HP",
                "Max HP Upgrade": "MAX +5",
                "Speed Boost": "SPEED++",
                "Damage Boost": "DMG +50%"
            }
            short_desc = emoji_map.get(item['name'], "???")
            
            button_text = f"{item['name']}\n{item['price']} COINS\n[{short_desc}]"
            
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(x, y, button_width, button_height),
                text=button_text,
                manager=self.ui_manager,
                container=self.shop_window,
                object_id=f'#item_{i}' if can_afford else f'#item_{i}_disabled'
            )
            self.shop_buttons.append(button)
        
        # Better close button with pixel aesthetic
        self.shop_close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(window_width - 180, window_height - 65, 160, 50),
            text='[ CLOSE ]',
            manager=self.ui_manager,
            container=self.shop_window,
            object_id='#close_button'
        )
    
    def close_shop_gui(self):
        """Close the shop window."""
        if self.shop_window is not None:
            self.shop_window.kill()
            self.shop_window = None
            self.shop_buttons = []
            self.shop_close_button = None
        
        self.shop_open = False
        pygame.event.set_grab(True)  # Re-grab mouse
        pygame.mouse.set_visible(True)
    
    def purchase_item(self, item_index):
        """Handle purchasing an item."""
        if item_index >= len(self.shop_items):
            return
        
        item = self.shop_items[item_index]
        price = item["price"]
        
        if self.coins >= price:
            self.coins -= price
            # Apply item effect
            if item["name"] == "Health Pack":
                self.player_hp = min(self.player_hp + 2, self.player_max_hp)  # Restore 2 HP
                print(f"Used Health Pack! HP: {self.player_hp}/{self.player_max_hp}")
            elif item["name"] == "Max HP Upgrade":
                self.player_max_hp += 5
                self.player_hp += 5  # Also heal the player
                print(f"Max HP increased! HP: {self.player_hp}/{self.player_max_hp}")
            elif item["name"] == "Speed Boost":
                if hasattr(self.player, 'speed'):
                    self.player.speed += 50
            elif item["name"] == "Damage Boost":
                # You can track this with a damage multiplier
                if not hasattr(self, 'damage_multiplier'):
                    self.damage_multiplier = 1.0
                self.damage_multiplier += 0.5
            
            # Refresh shop window to update coins display
            self.close_shop_gui()
            self.open_shop_gui()
    
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
                self.coins += 5  # Bonus coins for sparing
                self.dialogue_text = "* You showed mercy!"
            else:
                self.coins += 3  # Coins for defeating
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
                
                # Handle pygame_gui events
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if self.shop_window:
                        # Check which button was pressed
                        for i, button in enumerate(self.shop_buttons):
                            if event.ui_element == button:
                                self.purchase_item(i)
                                break
                        if event.ui_element == self.shop_close_button:
                            self.close_shop_gui()
                
                elif event.type == pygame_gui.UI_WINDOW_CLOSE:
                    if event.ui_element == self.shop_window:
                        self.close_shop_gui()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.shop_open:
                            # Close shop with ESC
                            self.close_shop_gui()
                        else:
                            pygame.event.set_grab(False)
                            self.running = False
                    elif event.key == pygame.K_e:
                        # Toggle shop when near
                        if self.nearby_shop and self.game_mode in ["EXPLORATION", "SURVIVAL_ONLY"] and not self.shop_open:
                            self.open_shop_gui()
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
                        # Start survival immediately on ENTER (no NPCs)
                        if event.key == pygame.K_RETURN:
                            self.game_mode = "SURVIVAL_ONLY"
                            self.story_mode = False
                    elif self.game_mode == "UNDERTALE_BATTLE":
                        self.handle_undertale_input(event)
                
                # Process pygame_gui events
                self.ui_manager.process_events(event)
                        
                if event.type == self.enemy_event and not self.game_over and self.game_mode in ["EXPLORATION", "SURVIVAL_ONLY"]:
                    if self.story_mode and self.story_enemies_spawned >= self.max_story_enemies:
                        pass
                    else:
                        stationary = self.story_mode
                        enemy = Enemy(choice(self.enemy_position), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, stationary)
                        
                        # Scale enemy speed based on coins (progression)
                        if self.coins <= 50:
                            enemy.speed = 200  # Much slower at start
                        elif self.coins <= 100:
                            enemy.speed = 250
                        elif self.coins <= 200:
                            enemy.speed = 300
                        elif self.coins <= 300:
                            enemy.speed = 350  # Default speed
                        else:
                            enemy.speed = 400  # Faster in late game
                        
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
                elif self.game_mode in ["EXPLORATION", "SURVIVAL_ONLY"]:
                    self.gun_timer()
                    # Check shop proximity
                    self.check_nearby_shop()
                    # Only update game logic if not frozen
                    if not self.freeze_timer and not self.shop_open:
                        # Update enemy spawn rate based on progression (coins)
                        self.update_enemy_spawn_rate()
                        
                        # THEME UPDATES
                        self.update_player_invisibility()
                        self.update_enemy_ghosts()
                        self.update_minimap_memory()
                        self.update_enemy_blinking(dt)
                        
                        self.input()
                        # Update sprites (movement/animation)
                        self.all_sprites.update(dt)
                        # Freeze enemies that are within the flashlight cone and pass light direction
                        if self.flashlight_enabled and hasattr(self, 'gun'):
                            light_direction = self.gun.player_dir
                            for enemy in self.enemy_sprites:
                                enemy.frozen_by_light = self.enemy_in_flashlight(enemy.rect.center)
                                enemy.light_direction = light_direction
                        self.bullet_collision()
                        if self.story_mode and self.game_mode == "EXPLORATION":
                            self.player_collision()
                        else:
                            # In survival mode, enemies deal 5 damage on contact
                            if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
                                self.take_damage(5)
                        
                        # Update damage cooldown
                        self.update_damage_cooldown()
                    # When shop is open, completely freeze the game (no updates)
                elif self.game_mode == "UNDERTALE_BATTLE":
                    # Only update battle if not frozen
                    if not self.freeze_timer:
                        self.update_undertale_battle(dt)
                        self.player_collision()
            
            if self.game_mode in ["INTRO", "EXPLORATION", "SURVIVAL_ONLY"]:
                self.screen.fill(('black'))
                
                if not self.game_over:
                    # Pass enemy visibility state to sprite group
                    self.all_sprites.enemy_visible = self.enemy_visible
                    self.all_sprites.draw(self.player.rect.center)
                    
                    # THEME: Draw enemy ghosts - DISABLED (user preference)
                    # self.draw_enemy_ghosts()
                    
                    # Night/flashlight overlay after world draw, before UI
                    if self.flashlight_enabled:
                        self.draw_flashlight_overlay()
                    
                    # THEME: Draw blinking enemies overlay
                    self.draw_blinking_enemies()
                    
                    # THEME: Draw player invisibility effect
                    if self.player_invisible:
                        self.draw_player_invisible()
                    
                    # THEME: Draw fading minimap
                    self.draw_minimap()
                    
                    # Display coins instead of score
                    coins_text = self.font.render(f"Coins: {self.coins}", True, (255, 215, 0))  # Gold color
                    self.screen.blit(coins_text, (10, 10))
                    
                    # HP display with damage indicator
                    hp_color = "red"
                    if self.damage_cooldown:
                        # Flash white when invincible
                        hp_color = (255, 255, 0) if (pygame.time.get_ticks() // 200) % 2 == 0 else (255, 100, 100)
                    hp_text = self.font.render(f"HP: {self.player_hp}/{self.player_max_hp}", True, hp_color)
                    self.screen.blit(hp_text, (10, 50))
                    
                    # Show invincibility indicator
                    if self.damage_cooldown:
                        inv_text = self.font.render("INVINCIBLE", True, (255, 255, 0))
                        self.screen.blit(inv_text, (10, 90))
                    
                    # Show shop interaction prompt
                    if self.nearby_shop and not self.shop_open:
                        prompt = self.font.render("Press E to open shop", True, (100, 255, 100))
                        prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
                        self.screen.blit(prompt, prompt_rect)
                    
                    # Draw dark overlay when shop is open
                    if self.shop_open:
                        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 180))
                        self.screen.blit(overlay, (0, 0))
                    
                    if self.game_mode == "INTRO":
                        # Minimal intro screen: press ENTER to begin
                        intro_title = self.title_font.render("Survival Mode", True, (16, 233, 160))
                        title_rect = intro_title.get_rect(center=(WINDOW_WIDTH//2, 80))
                        self.screen.blit(intro_title, title_rect)

                        prompt = self.font.render("Press ENTER to begin", True, (200, 200, 255))
                        prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH//2, 130))
                        self.screen.blit(prompt, prompt_rect)
                    
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
                        final_coins_text = self.title_font.render(f"Final Coins: {self.coins}", True, (255, 215, 0))
                        coins_rect = final_coins_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))
                        self.screen.blit(final_coins_text, coins_rect)
                    
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
            
            # Update and draw pygame_gui
            self.ui_manager.update(dt)
            self.ui_manager.draw_ui(self.screen)
            
            pygame.display.update()

        pygame.quit()
        
if __name__ == "__main__":
    game = Game()
    game.run()