import pygame
import sys
import subprocess
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

class StartScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game Menu - Choose Your Stage")
        self.clock = pygame.time.Clock()
        self.running = True
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, 'fonts', '04B_30__.TTF')
            if os.path.exists(font_path):
                self.title_font = pygame.font.Font(font_path, 72)
                self.menu_font = pygame.font.Font(font_path, 48)
                self.subtitle_font = pygame.font.Font(font_path, 32)
                print(f"Custom font loaded from: {font_path}")
            else:
                raise FileNotFoundError("Custom font not found")
        except Exception as e:
            print(f"Could not load custom font: {e}")
            self.title_font = pygame.font.Font(None, 72)
            self.menu_font = pygame.font.Font(None, 48)
            self.subtitle_font = pygame.font.Font(None, 32)
        
        self.menu_options = [
            {"text": "Stage 1", "action": self.start_stage1, "color": GREEN},
            {"text": "Stage 2", "action": self.start_stage2, "color": BLUE},
            {"text": "Quit", "action": self.quit_game, "color": RED}
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
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.menu_options[self.selected_option]["action"]()
                elif event.key == pygame.K_ESCAPE:
                    self.quit_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(self.button_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_option = i
                            self.menu_options[i]["action"]()
                            
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_option = i
    
    def draw(self):
        self.draw_gradient_background()
        
        title_text = self.title_font.render("SURVIVOR GAME", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.subtitle_font.render("Choose Your Adventure", True, LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 220))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        self.button_rects = []
        start_y = 300
        button_spacing = 100
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y + i * button_spacing
            
            button_width = 400
            button_height = 80
            button_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - button_width // 2,
                y_pos - button_height // 2,
                button_width,
                button_height
            )
            self.button_rects.append(button_rect)
            
            if i == self.selected_option:
                pygame.draw.rect(self.screen, option["color"], button_rect)
                pygame.draw.rect(self.screen, WHITE, button_rect, 4)
                text_color = WHITE
            else:
                pygame.draw.rect(self.screen, GRAY, button_rect)
                pygame.draw.rect(self.screen, option["color"], button_rect, 3)
                text_color = WHITE
            
            text_surface = self.menu_font.render(option["text"], True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        controls_text = [
            "Controls:",
            "↑↓ - Navigate menu",
            "Enter/Space - Select",
            "Esc - Quit"
        ]
        
        y_start = WINDOW_HEIGHT - 100
        for i, text in enumerate(controls_text):
            color = WHITE if i == 0 else LIGHT_GRAY
            font = self.subtitle_font if i == 0 else pygame.font.Font(None, 24)
            rendered_text = font.render(text, True, color)
            text_rect = rendered_text.get_rect(center=(WINDOW_WIDTH // 2, y_start + i * 25))
            self.screen.blit(rendered_text, text_rect)
        
        pygame.display.flip()
    
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
            
            python_exe = sys.executable
            if platform.system() == "Windows" and not python_exe.endswith('.exe'):
                if os.path.exists(python_exe + '.exe'):
                    python_exe = python_exe + '.exe'
            
            subprocess.run([python_exe, 'main.py'], 
                         cwd=stage1_path, check=True)
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
            
            python_exe = sys.executable
            if platform.system() == "Windows" and not python_exe.endswith('.exe'):
                if os.path.exists(python_exe + '.exe'):
                    python_exe = python_exe + '.exe'
            
            subprocess.run([python_exe, 'main.py'], 
                         cwd=stage2_path, check=True)
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