import pygame
import sys
import subprocess
import importlib.util
import os
import platform
from os.path import join

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 100, 200)
GREEN = (0, 150, 50)
RED = (200, 50, 50)
CYAN = (0, 200, 200)
GOLD = (255, 215, 0)
PURPLE = (150, 50, 200)
DARK_BLUE = (20, 30, 60)

class StartScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Survivor - Memory & Invisibility")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_view = "MENU"  # MENU or HELP
        self.help_scroll = 0
        self.max_help_scroll = 0
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, 'fonts', '04B_30__.TTF')
            if os.path.exists(font_path):
                self.title_font = pygame.font.Font(font_path, 72)
                self.menu_font = pygame.font.Font(font_path, 48)
                self.subtitle_font = pygame.font.Font(font_path, 32)
                self.small_font = pygame.font.Font(font_path, 20)
                self.tiny_font = pygame.font.Font(font_path, 16)
                self.gameF = pygame.font.Font(font_path, 60)
                print(f"Custom font loaded from: {font_path}")
            else:
                raise FileNotFoundError("Custom font not found")
        except Exception as e:
            print(f"Could not load custom font: {e}")
            self.title_font = pygame.font.Font(None, 62)
            self.menu_font = pygame.font.Font(None, 48)
            self.subtitle_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
            self.tiny_font = pygame.font.Font(None, 16)
        
        self.menu_options = [
            {"text": "Nightfall Survival", "action": self.start_stage1, "color": GREEN, "desc": "Flashlight combat in the dark"},
            {"text": "Memory Sequence", "action": self.start_stage2, "color": CYAN, "desc": "Test your memory under pressure"},
            {"text": "Help & Controls", "action": self.show_help, "color": GOLD, "desc": "Learn the game mechanics"},
            {"text": "Quit", "action": self.quit_game, "color": RED, "desc": "Exit to desktop"}
        ]
        
        self.selected_option = 0
        self.button_rects = []
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            music_path = os.path.join(current_dir, 'stage 1', 'audio', 'music.wav')
            if os.path.exists(music_path):
                self.menu_music = pygame.mixer.Sound(music_path)
                self.menu_music.set_volume(0.3)
                self.menu_music.play(loops=-1)
                print(f"Menu music loaded from: {music_path}")
            else:
                print(f"Music file not found at: {music_path}")
                self.menu_music = None
        except Exception as e:
            print(f"Could not load menu music: {e}")
            self.menu_music = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.current_view == "HELP":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        self.current_view = "MENU"
                        self.help_scroll = 0
                    elif event.key == pygame.K_UP:
                        self.help_scroll = max(0, self.help_scroll - 30)
                    elif event.key == pygame.K_DOWN:
                        self.help_scroll = min(self.max_help_scroll, self.help_scroll + 30)
                else:  # MENU
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.menu_options[self.selected_option]["action"]()
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.current_view == "HELP":
                    if event.button == 1:  # Left click anywhere to return
                        self.current_view = "MENU"
                        self.help_scroll = 0
                    elif event.button == 4:  # Scroll up
                        self.help_scroll = max(0, self.help_scroll - 30)
                    elif event.button == 5:  # Scroll down
                        self.help_scroll = min(self.max_help_scroll, self.help_scroll + 30)
                else:  # MENU
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        for i, rect in enumerate(self.button_rects):
                            if rect.collidepoint(mouse_pos):
                                self.selected_option = i
                                self.menu_options[i]["action"]()
                            
            elif event.type == pygame.MOUSEMOTION:
                if self.current_view == "MENU":
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(self.button_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_option = i
    
    def draw(self):
        if self.current_view == "HELP":
            self.draw_help_screen()
        else:
            self.draw_main_menu()
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        self.draw_gradient_background()
        
        # Animated title with glow effect
        title_text = self.title_font.render("SURVIVOR", True, GOLD)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        
        # Glow layers
        for offset in [4, 2]:
            glow = self.title_font.render("SURVIVOR", True, (100, 80, 0))
            glow_rect = glow.get_rect(center=(WINDOW_WIDTH // 2 + offset, 120 + offset))
            self.screen.blit(glow, glow_rect)
        
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.subtitle_font.render("Memory & Invisibility", True, CYAN)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 190))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        tagline = self.small_font.render("Two stages. Two unique challenges.", True, LIGHT_GRAY)
        tagline_rect = tagline.get_rect(center=(WINDOW_WIDTH // 2, 230))
        self.screen.blit(tagline, tagline_rect)
        
        # Menu buttons with descriptions
        self.button_rects = []
        start_y = 290
        button_spacing = 100
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y + i * button_spacing
            
            button_width = 500
            button_height = 75
            button_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - button_width // 2,
                y_pos - button_height // 2,
                button_width,
                button_height
            )
            self.button_rects.append(button_rect)
            
            # Draw button with modern style
            if i == self.selected_option:
                # Highlighted button with shadow
                shadow = pygame.Rect(button_rect.x + 4, button_rect.y + 4, button_rect.width, button_rect.height)
                pygame.draw.rect(self.screen, BLACK, shadow, border_radius=10)
                pygame.draw.rect(self.screen, option["color"], button_rect, border_radius=10)
                pygame.draw.rect(self.screen, WHITE, button_rect, 4, border_radius=10)
                text_color = WHITE
                desc_color = WHITE
            else:
                # Normal button
                pygame.draw.rect(self.screen, DARK_BLUE, button_rect, border_radius=10)
                pygame.draw.rect(self.screen, option["color"], button_rect, 2, border_radius=10)
                text_color = LIGHT_GRAY
                desc_color = GRAY
            
            # Button text
            text_surface = self.subtitle_font.render(option["text"], True, text_color)
            text_rect = text_surface.get_rect(center=(button_rect.centerx, button_rect.centery - 10))
            self.screen.blit(text_surface, text_rect)
            
            # Button description
            desc_surface = self.tiny_font.render(option["desc"], True, desc_color)
            desc_rect = desc_surface.get_rect(center=(button_rect.centerx, button_rect.centery + 18))
            self.screen.blit(desc_surface, desc_rect)
        
        # Footer controls
        controls_text = [
            "↑↓ Navigate  |  Enter/Space Select  |  Esc Quit"
        ]
        
        y_start = WINDOW_HEIGHT - 50
        for i, text in enumerate(controls_text):
            rendered_text = self.small_font.render(text, True, LIGHT_GRAY)
            text_rect = rendered_text.get_rect(center=(WINDOW_WIDTH // 2, y_start + i * 25))
            self.screen.blit(rendered_text, text_rect)
    
    def draw_help_screen(self):
        # Dark background with subtle gradient
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            color_value = int(35 * (1 - ratio))
            color = (color_value // 2, color_value // 3, color_value)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Create scrollable content surface with proper margins
        content_width = WINDOW_WIDTH - 200
        content_height = 2200
        content_surface = pygame.Surface((content_width, content_height), pygame.SRCALPHA)
        content_surface.fill((0, 0, 0, 0))
        
        y_offset = 10
        line_spacing = 28
        section_spacing = 45
        left_margin = 40
        
        def draw_text(text, font, color, x_center=True, indent=0):
            nonlocal y_offset
            rendered = font.render(text, True, color)
            if x_center:
                rect = rendered.get_rect(center=(content_surface.get_width() // 2, y_offset))
            else:
                rect = rendered.get_rect(x=left_margin + indent, y=y_offset)
            content_surface.blit(rendered, rect)
            y_offset += line_spacing
        
        def draw_section_title(text):
            nonlocal y_offset
            y_offset += section_spacing // 2
            # Draw section background
            title_bg = pygame.Rect(20, y_offset - 5, content_width - 40, 35)
            pygame.draw.rect(content_surface, (40, 40, 60, 180), title_bg, border_radius=5)
            draw_text(text, self.subtitle_font, GOLD)
            y_offset += 5
        
        # Title with box
        # title_box = pygame.Rect(content_width // 2 - 220, y_offset - 5, 440, 70)
        # pygame.draw.rect(content_surface, (30, 30, 50, 200), title_box, border_radius=12)
        # pygame.draw.rect(content_surface, GOLD, title_box, 3, border_radius=12)
        # draw_text("GAME GUIDE", self.gameF, WHITE)
        y_offset += 25
        
        # Theme explanation
        draw_section_title("GAME THEMES")
        draw_text("This game explores cognitive challenges:", self.small_font, LIGHT_GRAY)
        y_offset += 8

        # Helper: draw a dynamically sized, aligned theme box
        def draw_theme_box(title, title_color, border_color, bg_rgba, lines):
            nonlocal y_offset
            padding = 12
            line_gap = 4
            title_gap = 8
            # Prepare surfaces
            title_surf = self.small_font.render(title, True, title_color)
            line_surfs = [self.tiny_font.render(text, True, LIGHT_GRAY) for text in lines]
            content_h = title_surf.get_height() + title_gap
            if line_surfs:
                content_h += sum(s.get_height() for s in line_surfs) + line_gap * (len(line_surfs) - 1)
            box_h = padding * 2 + content_h
            box_rect = pygame.Rect(left_margin - 10, y_offset, content_width - 60, box_h)
            pygame.draw.rect(content_surface, bg_rgba, box_rect, border_radius=8)
            pygame.draw.rect(content_surface, border_color, box_rect, 2, border_radius=8)
            # Text positions
            tx = left_margin + 5
            ty = y_offset + padding
            content_surface.blit(title_surf, (tx, ty))
            y = ty + title_surf.get_height() + title_gap
            for s in line_surfs:
                content_surface.blit(s, (tx + 15, y))
                y += s.get_height() + line_gap
            # Advance
            y_offset += box_h + 16

        # Draw Stage 1 & Stage 2 theme boxes using dynamic sizing
        draw_theme_box(
            "STAGE 1: Invisibility", GREEN, GREEN, (20, 60, 20, 100), [
                "Fight in darkness with flashlight.",
                "Enemies freeze in light, hunt in dark.",
                "Manage vision under pressure.",
            ]
        )

        draw_theme_box(
            "STAGE 2: Memory Overload", CYAN, CYAN, (20, 40, 60, 100), [
                "Shoot enemies in correct sequence.",
                "Wrong order resets the level.",
                "Memory flash reveals numbers.",
            ]
        )
        
        # Stage 1 controls
        draw_section_title("STAGE 1: Nightfall")
        
        draw_text("CONTROLS", self.small_font, WHITE, False)
        y_offset += 5
        draw_text("WASD / Arrows - Move character", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Mouse - Aim flashlight & gun", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Click - Shoot enemies", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Enter - Start survival", self.tiny_font, LIGHT_GRAY, False, 20)
        y_offset += 12
        
        draw_text("GAMEPLAY", self.small_font, WHITE, False)
        y_offset += 5
        draw_text("Flashlight FREEZES enemies in beam", self.tiny_font, GREEN, False, 20)
        draw_text("Enemies move freely in darkness", self.tiny_font, RED, False, 20)
        draw_text("Shoot frozen enemies safely", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Reach 400 points to win", self.tiny_font, GOLD, False, 20)
        
        # Stage 2 controls
        draw_section_title("STAGE 2: Memory")
        
        draw_text("CONTROLS", self.small_font, WHITE, False)
        y_offset += 5
        draw_text("WASD / Arrows - Move & dodge", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Mouse - Aim and shoot", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Click - Shoot target", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("E - Toggle memory flash", self.tiny_font, CYAN, False, 20)
        draw_text("Shift - Show hitbox", self.tiny_font, LIGHT_GRAY, False, 20)
        y_offset += 12
        
        draw_text("GAMEPLAY PHASES", self.small_font, WHITE, False)
        y_offset += 5
        draw_text("1. SPAWNING - Enemies appear", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("2. SHOW - Memorize sequence (3s)", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("3. INPUT - Shoot in order", self.tiny_font, GOLD, False, 20)
        draw_text("4. Wrong order? Level restarts", self.tiny_font, RED, False, 20)
        y_offset += 12
        
        draw_text("MEMORY FLASH", self.small_font, CYAN, False)
        y_offset += 5
        draw_text("Press E to reveal numbers", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("90 seconds total capacity", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Starts 100%, +10% per level", self.tiny_font, GREEN, False, 20)
        draw_text("Use strategically!", self.tiny_font, GOLD, False, 20)
        
        # Tips section
        draw_section_title("PRO TIPS")
        
        draw_text("Stage 1", self.small_font, GREEN, False)
        y_offset += 5
        draw_text("Keep moving constantly", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Sweep light in arcs", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Back up from close enemies", self.tiny_font, LIGHT_GRAY, False, 20)
        y_offset += 12
        
        draw_text("Stage 2", self.small_font, CYAN, False)
        y_offset += 5
        draw_text("Focus during SHOW phase", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Use flash wisely", self.tiny_font, LIGHT_GRAY, False, 20)
        draw_text("Keep moving from bees", self.tiny_font, LIGHT_GRAY, False, 20)
        
        # Footer
        draw_section_title("NAVIGATION")
        y_offset += 5
        
        footer_box = pygame.Rect(left_margin - 10, y_offset - 5, content_width - 60, 65)
        pygame.draw.rect(content_surface, (60, 50, 20, 120), footer_box, border_radius=8)
        pygame.draw.rect(content_surface, GOLD, footer_box, 2, border_radius=8)
        
        draw_text("ESC or Click - Return to menu", self.small_font, GOLD, False, 15)
        draw_text("UP/DOWN or Scroll - Navigate", self.tiny_font, LIGHT_GRAY, False, 15)
        
        # Calculate max scroll
        self.max_help_scroll = max(0, y_offset - (WINDOW_HEIGHT - 150))
        
        # Draw semi-transparent background panel
        panel_rect = pygame.Rect(80, 40, WINDOW_WIDTH - 160, WINDOW_HEIGHT - 80)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((15, 20, 35, 230))
        self.screen.blit(panel_surface, (panel_rect.x, panel_rect.y))
        pygame.draw.rect(self.screen, GOLD, panel_rect, 3, border_radius=15)
        
        # Blit scrolled content to screen
        visible_rect = pygame.Rect(0, self.help_scroll, content_width, WINDOW_HEIGHT - 120)
        self.screen.blit(content_surface, (100, 60), visible_rect)
        
        # Scroll indicators with better visibility
        if self.help_scroll > 0:
            up_indicator = pygame.Rect(WINDOW_WIDTH // 2 - 80, 50, 160, 30)
            pygame.draw.rect(self.screen, (40, 40, 60, 200), up_indicator, border_radius=5)
            up_text = self.small_font.render("^ Scroll Up", True, WHITE)
            up_rect = up_text.get_rect(center=(WINDOW_WIDTH // 2, 65))
            self.screen.blit(up_text, up_rect)
        
        if self.help_scroll < self.max_help_scroll:
            down_indicator = pygame.Rect(WINDOW_WIDTH // 2 - 90, WINDOW_HEIGHT - 45, 180, 30)
            pygame.draw.rect(self.screen, (40, 40, 60, 200), down_indicator, border_radius=5)
            down_text = self.small_font.render("v More Below", True, WHITE)
            down_rect = down_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
            self.screen.blit(down_text, down_rect)
    
    def draw_gradient_background(self):
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            color_value = int(50 * (1 - ratio))
            color = (color_value // 3, color_value // 2, color_value)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
    
    def start_stage1(self):
        print("Starting Stage 1...")
        pygame.mixer.stop()
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            stage1_path = os.path.join(current_dir, 'stage 1', 'code')
            
            stage1_path = os.path.normpath(stage1_path)
            
            if not os.path.exists(stage1_path):
                print(f"Stage 1 path not found: {stage1_path}")
                return
                
            print(f"Running Stage 1 from: {stage1_path}")
            
            # In web (pygbag / emscripten), subprocess is not supported.
            if sys.platform == "emscripten":
                main_file = os.path.join(stage1_path, 'main.py')
                if not os.path.isfile(main_file):
                    print(f"Stage 1 main not found: {main_file}")
                    return
                # Dynamically load and run Game().run() from file
                spec = importlib.util.spec_from_file_location("stage1_main", main_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'Game'):
                        game = module.Game()
                        game.run()
                    elif hasattr(module, 'main'):
                        module.main()
                    else:
                        print("Stage 1 module has no Game or main entry point")
                else:
                    print("Failed to import Stage 1 module dynamically")
            else:
                # Desktop: spawn a subprocess so working dir is correct
                python_exe = sys.executable
                if platform.system() == "Windows" and not python_exe.endswith('.exe'):
                    if os.path.exists(python_exe + '.exe'):
                        python_exe = python_exe + '.exe'
                subprocess.run([python_exe, 'main.py'], cwd=stage1_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Stage 1 exited with error code: {e.returncode}")
        except Exception as e:
            print(f"Error starting Stage 1: {e}")
        finally:
            try:
                if self.menu_music:
                    self.menu_music.play(loops=-1)
            except:
                pass
    
    def start_stage2(self):
        print("Starting Stage 2...")
        pygame.mixer.stop()
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            stage2_path = os.path.join(current_dir, 'stage 2', 'code')
            
            stage2_path = os.path.normpath(stage2_path)
            
            if not os.path.exists(stage2_path):
                print(f"Stage 2 path not found: {stage2_path}")
                return
                
            print(f"Running Stage 2 from: {stage2_path}")
            
            # In web (pygbag / emscripten), subprocess is not supported.
            if sys.platform == "emscripten":
                main_file = os.path.join(stage2_path, 'main.py')
                if not os.path.isfile(main_file):
                    print(f"Stage 2 main not found: {main_file}")
                    return
                # Dynamically load and run Game().run() from file
                spec = importlib.util.spec_from_file_location("stage2_main", main_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'Game'):
                        game = module.Game()
                        game.run()
                    elif hasattr(module, 'main'):
                        module.main()
                    else:
                        print("Stage 2 module has no Game or main entry point")
                else:
                    print("Failed to import Stage 2 module dynamically")
            else:
                # Desktop: spawn a subprocess so working dir is correct
                python_exe = sys.executable
                if platform.system() == "Windows" and not python_exe.endswith('.exe'):
                    if os.path.exists(python_exe + '.exe'):
                        python_exe = python_exe + '.exe'
                subprocess.run([python_exe, 'main.py'], cwd=stage2_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Stage 2 exited with error code: {e.returncode}")
        except Exception as e:
            print(f"Error starting Stage 2: {e}")
        finally:
            try:
                if self.menu_music:
                    self.menu_music.play(loops=-1)
            except:
                pass
    
    def quit_game(self):
        self.running = False
    
    def show_help(self):
        """Switch to help screen view"""
        self.current_view = "HELP"
        self.help_scroll = 0
    
    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    start_screen = StartScreen()
    start_screen.run()

if __name__ == "__main__":
    main()