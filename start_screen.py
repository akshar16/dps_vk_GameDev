import pygame
import sys
import subprocess
from os.path import join

# Initialize pygame
pygame.init()

# Constants
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
        
        # Load fonts
        try:
            self.title_font = pygame.font.Font(join('fonts', '04B_30__.TTF'), 72)
            self.menu_font = pygame.font.Font(join('fonts', '04B_30__.TTF'), 48)
            self.subtitle_font = pygame.font.Font(join('fonts', '04B_30__.TTF'), 32)
        except:
            # Fallback to default fonts if custom font not found
            self.title_font = pygame.font.Font(None, 72)
            self.menu_font = pygame.font.Font(None, 48)
            self.subtitle_font = pygame.font.Font(None, 32)
        
        # Menu options
        self.menu_options = [
            {"text": "Stage 1", "action": self.start_stage1, "color": GREEN},
            {"text": "Stage 2", "action": self.start_stage2, "color": BLUE},
            {"text": "Quit", "action": self.quit_game, "color": RED}
        ]
        
        self.selected_option = 0
        self.button_rects = []
        
        # Load background music if available
        try:
            self.menu_music = pygame.mixer.Sound(join('stage 1 ', 'audio', 'music.wav'))
            self.menu_music.set_volume(0.3)
            self.menu_music.play(loops=-1)
        except:
            pass  # No music file found
    
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
                if event.button == 1:  # Left click
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
        # Clear screen with gradient background
        self.draw_gradient_background()
        
        # Draw title
        title_text = self.title_font.render("SURVIVOR GAME", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.subtitle_font.render("Choose Your Adventure", True, LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 220))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw menu options
        self.button_rects = []
        start_y = 300
        button_spacing = 100
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y + i * button_spacing
            
            # Create button rectangle
            button_width = 400
            button_height = 80
            button_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - button_width // 2,
                y_pos - button_height // 2,
                button_width,
                button_height
            )
            self.button_rects.append(button_rect)
            
            # Draw button
            if i == self.selected_option:
                # Highlighted button
                pygame.draw.rect(self.screen, option["color"], button_rect)
                pygame.draw.rect(self.screen, WHITE, button_rect, 4)
                text_color = WHITE
            else:
                # Normal button
                pygame.draw.rect(self.screen, GRAY, button_rect)
                pygame.draw.rect(self.screen, option["color"], button_rect, 3)
                text_color = WHITE
            
            # Draw button text
            text_surface = self.menu_font.render(option["text"], True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Draw controls info
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
        """Draw a simple gradient background"""
        for y in range(WINDOW_HEIGHT):
            # Create gradient from dark blue to black
            ratio = y / WINDOW_HEIGHT
            color_value = int(50 * (1 - ratio))
            color = (color_value // 3, color_value // 2, color_value)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
    
    def start_stage1(self):
        """Start Stage 1 of the game"""
        print("Starting Stage 1...")
        pygame.mixer.stop()  # Stop menu music
        try:
            # Run stage 1 from its code directory
            subprocess.run([sys.executable, 'main.py'], 
                         cwd='stage 1 /code')
        except Exception as e:
            print(f"Error starting Stage 1: {e}")
        finally:
            # Return to menu
            try:
                self.menu_music.play(loops=-1)
            except:
                pass
    
    def start_stage2(self):
        """Start Stage 2 of the game"""
        print("Starting Stage 2...")
        pygame.mixer.stop()  # Stop menu music
        try:
            # Run stage 2 from its code directory
            subprocess.run([sys.executable, 'main.py'], 
                         cwd=' stage 2/code')
        except Exception as e:
            print(f"Error starting Stage 2: {e}")
        finally:
            # Return to menu
            try:
                self.menu_music.play(loops=-1)
            except:
                pass
    
    def quit_game(self):
        """Quit the game"""
        self.running = False
    
    def run(self):
        """Main game loop"""
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