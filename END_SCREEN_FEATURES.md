# End Screen Features - Both Stages

## Overview
Both Stage 1 and Stage 2 now feature comprehensive end screens that display final scores and game statistics when the player completes or fails a stage.

## Stage 1 End Screen Features

### Score Display
- **Final Score**: Prominently shows `Final Score: {score}` 
- **Real-time Score**: Displays current score during gameplay at top-left
- **Score Sources**: 
  - +1 for each enemy defeated
  - +3 for Undertale battle victories
  - +5 for showing mercy (sparing enemies)

### Multiple End Types
1. **Victory Screen** (Score ≥ 400)
   - Green "VICTORY!" title
   - "Quest Complete!" subtitle
   - Final score display

2. **Story Completion Screen**
   - Golden "REFLECTION" title
   - Deep philosophical message about choices
   - Focus on meaning over score

3. **Game Over Screen**
   - Red "GAME OVER" title
   - Standard score display
   - Restart options

### Navigation
- **ESC**: Return to main menu
- **Q**: Quit game completely

## Stage 2 End Screen Features

### Score Display
- **Final Score**: Shows `Final Score: {score}` in large title font
- **Live Score**: Current score displayed during gameplay
- **Score Sources**:
  - +1 for regular enemies
  - +10 for TouhouBee enemies
  - +100 for boss (Queen Bee) defeat

### Victory/Defeat Screens

#### Victory Screen
- **Title**: Golden "VICTORY!" text
- **Subtitle**: "Stage 2 Complete!" in green
- **Victory Message**: "The Queen Bee has been defeated!"
- **Boss Status**: "Boss Battle Complete!" if boss was defeated
- **Stats**: Lives remaining display

#### Defeat Screen  
- **Title**: Red "GAME OVER" text
- **Defeat Message**: "The Queen Bee proved too powerful..."
- **Stats**: Lives remaining at time of defeat

### Enhanced Features
- **Lives Display**: Shows remaining lives on end screen
- **Boss Status**: Special message for boss completion
- **Professional Layout**: Proper spacing and color-coded messages
- **Performance Stats**: Additional gameplay statistics

### Navigation
- **ESC**: Return to main menu (start_screen.py)
- **Q**: Quit game completely

## Technical Implementation

### Stage 1 End Screen
```python
# Multiple end screen types with different messages
if hasattr(self, 'story_complete') and self.story_complete:
    # Philosophical reflection screen
elif hasattr(self, 'victory') and self.victory:
    # Victory celebration screen  
else:
    # Standard game over screen

# Score always displayed except in story completion mode
final_score_text = self.title_font.render(f"Final Score: {self.score}", True, "white")
```

### Stage 2 End Screen  
```python
def draw_game_over(self):
    # Victory vs defeat differentiation
    if self.victory:
        # Victory screen with boss completion details
    else:
        # Defeat screen with encouraging message
        
    # Prominent score display
    final_score_text = self.title_font.render(f"Final Score: {self.score}", True, 'white')
    
    # Additional stats
    performance_text = self.font.render(f"Lives Remaining: {self.lives}", True, (200, 200, 255))
```

## Scoring Systems

### Stage 1 Scoring
- **Philosophy-Based**: Emphasizes choice and mercy
- **Bonus Points**: Rewards non-violent solutions
- **Victory Threshold**: 400 points for automatic victory
- **Undertale Integration**: Score reflects battle choices

### Stage 2 Scoring
- **Action-Based**: Rewards combat skill and survival
- **Escalating Points**: Higher value targets give more points
- **Boss Focus**: Major score boost for boss defeat (100 points)
- **Touhou Style**: Fast-paced scoring system

## User Experience

### Consistency
- Both stages use the same navigation (ESC/Q)
- Similar visual styling with stage-appropriate themes
- Professional fonts and color schemes
- Clear score prominence

### Feedback
- **Immediate**: Live score during gameplay
- **Comprehensive**: Detailed end screen statistics  
- **Encouraging**: Positive messaging even in defeat
- **Informative**: Clear next steps (menu/quit options)

### Visual Design
- **Stage 1**: More philosophical and story-focused
- **Stage 2**: More action-oriented and achievement-focused
- **Both**: Professional presentation with proper spacing

## Return to Menu Integration
Both stages properly integrate with the start screen system:
- **ESC key**: Returns to main menu (`start_screen.py`)
- **Seamless transition**: Maintains game flow
- **Proper cleanup**: Cleans up resources before returning

## Future Enhancements
Potential improvements for end screens:
- **Statistics tracking**: Enemies defeated, accuracy, etc.
- **Achievement system**: Special accomplishments
- **Leaderboards**: High score tracking
- **Time statistics**: Completion time display
- **Detailed breakdowns**: Score source analysis

Both stages now provide complete, professional end screen experiences that properly display scores and guide players back to the main menu for continued gameplay!
