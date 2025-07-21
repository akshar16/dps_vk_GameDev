# Two-Stage Adventure Game

A Python game featuring two distinct gameplay experiences:
- **Stage 1**: Undertale-inspired mechanics with story mode and survival mode
- **Stage 2**: Touhou-style bullet hell action

## Features

### Stage 1: Undertale-Style Adventure
- **Story Mode**: Interactive NPCs, turn-based battles with ATTACK/TALK/HEAL/SPARE options
- **Survival Mode**: Classic survival gameplay with endless enemy waves
- **Undertale Battle System**: Soul mechanics with blue/orange bullet patterns
- **Multiple Endings**: Victory, story completion, and defeat screens

### Stage 2: Touhou Bullet Hell
- Fast-paced bullet hell gameplay
- Enemy waves with varying patterns
- Score-based progression
- Lives system with end screens

## Controls

### General
- **Arrow Keys/WASD**: Move player
- **Mouse**: Aim and shoot (Stage 1)
- **Shift**: Show hitbox (Stage 2)
- **Space**: Interact with NPCs, confirm menu selections
- **ESC**: Return to menu (on game over screens)
- **Q**: Quit game (on game over screens)

### Undertale Battles (Stage 1)
- **Arrow Keys/WASD**: Navigate menus and move soul
- **Space/Enter**: Confirm selection
- **Left/Right**: Select battle options (ATTACK, TALK, HEAL, SPARE)

## Requirements

- Python 3.x
- pygame-ce 2.5.5
- pytmx

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/two-stage-adventure-game.git
cd two-stage-adventure-game
```

2. Install dependencies:
```bash
pip install pygame-ce pytmx
```

3. Run the game:

**Windows:**
```batch
run_game.bat
```
Or:
```cmd
python start_screen.py
```

**Mac/Linux:**
```bash
python3 start_screen.py
```
Or:
```bash
./run_game.sh
```

**Cross-platform Python launcher:**
```bash
python run_game.py
```
```

## Game Structure

```
├── start_screen.py          # Main menu and stage launcher
├── fonts/                   # Custom fonts
│   └── 04B_30__.TTF
├── stage 1/                 # Undertale-style stage
│   ├── code/               # Game logic
│   ├── audio/              # Sound effects and music
│   ├── data/               # Maps and tilesets
│   └── images/             # Sprites and graphics
└── stage 2/                # Touhou-style stage
    ├── code/               # Game logic
    ├── audio/              # Sound effects and music
    ├── data/               # Maps and tilesets
    └── images/             # Sprites and graphics
```

## Gameplay Tips

### Stage 1
- Talk to NPCs to choose between Story Mode and Survival Mode
- In Story Mode, try using SPARE after talking to enemies
- Blue bullets hurt only when moving, orange bullets hurt only when still
- Reach 400 points or complete the story for victory

#### Story Mode Features
- **Story Guide NPC**: A wise character positioned behind the player that introduces meaningful gameplay
- **Limited enemies**: Only 10 stationary enemies spawn for thoughtful encounters
- **Undertale-style combat**: ATTACK/TALK/HEAL/SPARE options with bullet hell defense
- **Philosophical themes**: Focus on choice, compassion, and understanding over violence
- **Enhanced dialogue system**: Improved UI with proper spacing and character-specific formatting
- **Multiple endings**: Victory, story completion with deep reflection, or determination failure

#### Survival Mode Features
- **Combat Instructor NPC**: Positioned to the left of the player for battle training
- **Endless enemy waves**: Classic survival gameplay with moving enemies
- **Score-based progression**: Aim for high scores while surviving as long as possible
- **Traditional combat**: Focus on weapon skills and movement

### Stage 2
- Use Shift to see your precise hitbox
- Focus on dodging rather than shooting constantly
- Survive as long as possible to achieve high scores

## Technical Features

### Advanced Game Mechanics
- **Undertale-style combat system** with soul mechanics and bullet patterns
- **Cross-platform path handling** for Windows and Mac compatibility
- **Dynamic sprite animation** with frame-based enemy movements
- **Collision detection** using pygame masks for pixel-perfect accuracy
- **Audio system** with background music and sound effects
- **Custom font integration** with fallback options

### End Screen System
Both stages feature comprehensive end screens with:
- **Score tracking** and final score display
- **Multiple ending types** (Victory, Story Completion, Game Over)
- **Platform-specific controls** (ESC to return, Q to quit)
- **Philosophical messaging** for story mode completion

### NPC Dialogue System
- **Interactive NPCs** with character-specific formatting
- **Enhanced dialogue boxes** with proper spacing and word wrapping
- **Branching storylines** leading to different game modes
- **Visual character representation** with scaled sprites

## Credits

Built with Python and pygame-ce. Features inspired by Undertale and Touhou series.

## License

This project is open source and available under the MIT License.
- **Smooth Controls**: Responsive player movement and shooting

## Requirements

- Python 3.6+
- Pygame
- pytmx (for tilemap loading)

## Installation

1. Make sure you have Python installed
2. Install required packages:
   ```bash
   pip install pygame pytmx
   ```
3. Run the game:
   ```bash
   python start_screen.py
   ```

## File Structure

```
├── start_screen.py      # Main menu/start screen
├── run_game.py         # Game launcher
├── stage 1/            # First game stage
│   ├── code/           # Stage 1 game code
│   ├── audio/          # Sound effects and music
│   ├── images/         # Sprites and graphics
│   └── data/           # Maps and tilesets
├── stage 2/            # Second game stage
│   ├── code/           # Stage 2 game code
│   ├── audio/          # Sound effects and music
│   ├── images/         # Sprites and graphics
│   └── data/           # Maps and tilesets
└── fonts/              # Game fonts
```

## Troubleshooting

- If you get import errors, make sure all required packages are installed
- If fonts don't load properly, the game will fall back to default system fonts
- If audio doesn't work, check that your audio files are present in the audio folders
- Make sure you're running the game from the main directory containing start_screen.py

Enjoy the game!
