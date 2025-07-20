import pygame
from settings import *
import os

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, name, dialogue, npc_type, groups, game):
        super().__init__(groups)
        
        # Store reference to game for base_path
        self.game = game
        
        # Create different sprites based on NPC type
        if npc_type == "bee":
            # Load bee sprites from local folder
            try:
                bee_frames = []
                for i in range(2):  # bee has 0.png and 1.png
                    bee_path = os.path.join(game.base_path, 'images', 'bee', f'{i}.png')
                    bee_surface = pygame.image.load(bee_path).convert_alpha()
                    # Scale up the bee to make it more visible as an NPC
                    bee_surface = pygame.transform.scale(bee_surface, (64, 64))
                    bee_frames.append(bee_surface)
                self.frames = bee_frames
                self.frame_index = 0
                self.image = self.frames[0]
                self.animation_speed = 5
            except Exception as e:
                print(f"Could not load bee images: {e}")
                # Fallback: Create a bee-like sprite
                self.image = pygame.Surface((32, 32))
                self.image.fill((255, 255, 0))  # Yellow bee
                pygame.draw.circle(self.image, (0, 0, 0), (16, 16), 12)
                pygame.draw.circle(self.image, (255, 255, 0), (16, 16), 10)
                # Add stripes
                for i in range(3):
                    y = 8 + i * 6
                    pygame.draw.rect(self.image, (0, 0, 0), (6, y, 20, 2))
                self.frames = [self.image]
                self.frame_index = 0
                self.animation_speed = 0
            
        elif npc_type == "dog":
            # Load dog sprite from local folder
            try:
                dog_path = os.path.join(game.base_path, 'images', 'dog', '0.png')
                dog_surface = pygame.image.load(dog_path).convert_alpha()
                # Scale up the dog to make it more visible as an NPC
                dog_surface = pygame.transform.scale(dog_surface, (64, 64))
                self.frames = [dog_surface]
                self.frame_index = 0
                self.image = self.frames[0]
                self.animation_speed = 0
            except Exception as e:
                print(f"Could not load dog image: {e}")
                # Fallback: Enhanced dog sprite
                self.image = pygame.Surface((48, 40))
                self.image.set_colorkey((0, 0, 0))  # Make black transparent
                self.image.fill((0, 0, 0))  # Fill with transparent color
                
                # Dog body (oval)
                pygame.draw.ellipse(self.image, (139, 69, 19), (12, 20, 28, 16))
                
                # Dog head (circle)
                pygame.draw.circle(self.image, (139, 69, 19), (24, 14), 12)
                
                # Dog ears (triangles) - floppy ears
                ear_points1 = [(16, 12), (12, 4), (20, 8)]
                ear_points2 = [(32, 12), (36, 4), (28, 8)]
                pygame.draw.polygon(self.image, (101, 67, 33), ear_points1)
                pygame.draw.polygon(self.image, (101, 67, 33), ear_points2)
                
                # Dog eyes
                pygame.draw.circle(self.image, (0, 0, 0), (21, 12), 2)
                pygame.draw.circle(self.image, (0, 0, 0), (27, 12), 2)
                pygame.draw.circle(self.image, (255, 255, 255), (21, 11), 1)
                pygame.draw.circle(self.image, (255, 255, 255), (27, 11), 1)
                
                # Dog nose
                pygame.draw.circle(self.image, (0, 0, 0), (24, 16), 2)
                
                # Dog mouth
                pygame.draw.arc(self.image, (0, 0, 0), (20, 16, 8, 6), 0, 3.14, 2)
                
                # Dog tail (will animate)
                pygame.draw.ellipse(self.image, (139, 69, 19), (40, 18, 6, 12))
                
                # Dog legs
                pygame.draw.rect(self.image, (101, 67, 33), (15, 32, 4, 8))
                pygame.draw.rect(self.image, (101, 67, 33), (22, 32, 4, 8))
                pygame.draw.rect(self.image, (101, 67, 33), (30, 32, 4, 8))
                pygame.draw.rect(self.image, (101, 67, 33), (37, 32, 4, 8))
                
                self.frames = [self.image.copy()]  # Store original for animation
                self.frame_index = 0
                self.animation_speed = 0
            
        else:  # fallback type
            # Generic NPC
            self.image = pygame.Surface((32, 48))
            self.image.fill((255, 150, 100))  # Orange for generic NPC
            # Add a simple face
            pygame.draw.circle(self.image, (255, 255, 255), (16, 12), 8)
            pygame.draw.circle(self.image, (0, 0, 0), (13, 10), 2)
            pygame.draw.circle(self.image, (0, 0, 0), (19, 10), 2)
            pygame.draw.arc(self.image, (0, 0, 0), (11, 12, 10, 6), 0, 3.14, 2)
            self.frames = [self.image]
            self.frame_index = 0
            self.animation_speed = 0
            
        self.rect = self.image.get_rect(topleft=pos)
        self.name = name
        self.dialogue = dialogue
        self.npc_type = npc_type
        self.interacting = False
        
        # Animation timers
        self.animation_timer = 0
        self.tail_offset = 0
        
    def update(self, dt):
        """Update NPC animations"""
        self.animation_timer += dt * 1000
        
        if self.npc_type == "bee" and len(self.frames) > 1:
            # Bee wing flapping animation
            if self.animation_timer >= 150:  # Change frame every 150ms
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                
        elif self.npc_type == "dog":
            # Dog tail wagging animation
            if self.animation_timer >= 300:  # Wag every 300ms
                self.animation_timer = 0
                self.tail_offset = 1 if self.tail_offset == 0 else 0
                
                # Animate tail wagging
                tail_x = 40 + (self.tail_offset * 3)
                tail_y = 18 + (self.tail_offset * 2)
                pygame.draw.ellipse(self.image, (139, 69, 19), (tail_x, tail_y, 6, 12))
    
    def get_interaction_rect(self):
        """Get the interaction area around the NPC"""
        return self.rect.inflate(40, 40)

class NPCDialogue:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.current_npc = None
        self.dialogue_text = ""
        self.dialogue_lines = []
        self.current_line = 0
        
    def start_dialogue(self, npc):
        """Start dialogue with an NPC"""
        self.active = True
        self.current_npc = npc
        self.dialogue_lines = npc.dialogue
        self.current_line = 0
        self.dialogue_text = self.dialogue_lines[0] if self.dialogue_lines else ""
        
    def next_line(self):
        """Move to next dialogue line"""
        self.current_line += 1
        if self.current_line < len(self.dialogue_lines):
            self.dialogue_text = self.dialogue_lines[self.current_line]
        else:
            self.end_dialogue()
            
    def end_dialogue(self):
        """End dialogue and trigger NPC action"""
        if self.current_npc:
            if self.current_npc.npc_type in ["survival", "bee"]:
                # Start original survival game mode
                self.game.game_mode = "SURVIVAL_ONLY"
                self.game.story_mode = False
            elif self.current_npc.npc_type in ["story", "dog"]:
                # Start story mode with Undertale mechanics
                self.game.game_mode = "EXPLORATION"
                self.game.story_mode = True
                
        self.active = False
        self.current_npc = None
        self.dialogue_text = ""
        
    def draw(self, surface):
        """Draw dialogue box with improved layout"""
        if self.active and self.dialogue_text:
            # Larger dialogue box with better positioning
            dialogue_box = pygame.Rect(30, WINDOW_HEIGHT - 150, WINDOW_WIDTH - 60, 130)
            pygame.draw.rect(surface, (0, 0, 0), dialogue_box)
            pygame.draw.rect(surface, (255, 255, 255), dialogue_box, 3)
            
            # Create smaller fonts for better readability
            try:
                # Try to use the game's font but smaller
                small_font = pygame.font.Font(None, 24)
                tiny_font = pygame.font.Font(None, 20)
            except:
                # Fallback to default fonts
                small_font = pygame.font.Font(None, 24)
                tiny_font = pygame.font.Font(None, 20)
            
            # NPC name with special styling for dog and bee
            if self.current_npc:
                if self.current_npc.npc_type == "dog":
                    name_color = (255, 215, 0)  # Gold for dog
                    name_prefix = "🐕 "
                elif self.current_npc.npc_type == "bee":
                    name_color = (255, 255, 100)  # Yellow for bee
                    name_prefix = "🐝 "
                else:
                    name_color = (255, 255, 100)  # Default yellow
                    name_prefix = ""
                
                name_text = small_font.render(f"{name_prefix}{self.current_npc.name}", True, name_color)
                surface.blit(name_text, (dialogue_box.x + 15, dialogue_box.y + 10))
            
            # Dialogue text (word wrap for long text)
            words = self.dialogue_text.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                if small_font.size(test_line)[0] < dialogue_box.width - 30:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            # Draw lines with better spacing
            for i, line in enumerate(lines[:3]):  # Max 3 lines
                line_surface = small_font.render(line, True, (255, 255, 255))
                surface.blit(line_surface, (dialogue_box.x + 15, dialogue_box.y + 45 + i * 30))
            
            # Continue indicator - positioned to fit within dialogue box
            if self.current_line < len(self.dialogue_lines) - 1:
                continue_text = tiny_font.render("Press SPACE to continue...", True, (200, 200, 200))
                # Position text properly within the dialogue box
                text_width = continue_text.get_width()
                surface.blit(continue_text, (dialogue_box.x + dialogue_box.width - text_width - 15, dialogue_box.y + dialogue_box.height - 30))
            else:
                end_text = tiny_font.render("Press SPACE to start!", True, (100, 255, 100))
                text_width = end_text.get_width()
                surface.blit(end_text, (dialogue_box.x + dialogue_box.width - text_width - 15, dialogue_box.y + dialogue_box.height - 30))
