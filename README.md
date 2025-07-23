# DPS Saket Game - Two-Stage Adventure

A Python-based two-stage adventure game featuring distinct gameplay experiences inspired by classic indie games. Built with pygame-ce and featuring custom pixel art, immersive audio, and engaging mechanics.

## 🎮 Game Overview

### Stage 1: Undertale-Style Adventure
- **Story Mode**: Interactive NPCs with meaningful dialogue and choice-based gameplay
- **Survival Mode**: Classic survival mechanics with endless enemy waves  
- **Turn-based Combat**: ATTACK/TALK/HEAL/SPARE options with bullet hell defense phases
- **Soul Mechanics**: Blue/orange bullet patterns requiring strategic movement
- **Multiple Endings**: Victory, story completion, and philosophical reflection paths

### Stage 2: Touhou-Style Bullet Hell
- **Intense Bullet Hell Action**: Fast-paced dodging with precise hitbox mechanics
- **Dynamic Enemy Spawning**: Bees and worms with unique attack patterns
- **Score-Based Progression**: High score tracking with performance metrics
- **Lives System**: Heart-based health with invulnerability frames
- **Visual Effects**: Freeze effects, damage indicators, and particle systems

## 🎯 Controls

### Universal Controls
- **Arrow Keys/WASD**: Move player character
- **ESC**: Return to main menu (from game over screens)
- **Q**: Quit game (from game over screens)

### Stage 1 Specific
- **Mouse**: Aim and shoot weapons
- **Space**: Interact with NPCs and confirm menu selections
- **Arrow Keys**: Navigate battle menus and move soul during bullet hell phases
- **Enter/Space**: Confirm battle selections (ATTACK/TALK/HEAL/SPARE)

### Stage 2 Specific  
- **Left Shift**: Display precise hitbox (small white circle)
- **Mouse**: Aim and shoot at enemies
- **Movement**: Precise dodging for bullet patterns

## 📋 System Requirements

- **Python**: 3.7+ (tested with 3.13)
- **pygame-ce**: 2.5.0 or higher
- **pytmx**: 3.21.7 or higher (for tilemap support)
- **Platform**: Windows, macOS, Linux compatible
- **Audio**: Sound card for music and effects

## 🚀 Installation & Setup

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/akshar16/dps_saket.git
   cd dps_saket
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or manually install:
   ```bash
   pip install pygame-ce>=2.5.0 pytmx>=3.21.7
   ```

3. **Run the game:**
   ```bash
   python main.py
   ```
   Or directly:
   ```bash
   python start_screen.py
   ```

### Alternative Execution (Windows)
- Double-click `DPS_rohini.exe` for direct execution (Windows only)

## 📁 Project Structure

```
dps_saket/
├── main.py                 # Game launcher with error handling
├── start_screen.py         # Main menu and stage selection
├── requirements.txt        # Python dependencies
├── DPS_rohini.exe         # Windows executable
├── TROUBLESHOOTING.md     # Common issues and solutions
├── fonts/                 # Custom game fonts
│   └── 04B_30__.TTF      # Pixel-style font
├── hearts/               # UI elements
│   ├── full_heart.png    # Life indicator (full)
│   └── empety_heart.png  # Life indicator (empty)
├── stage 1/              # Undertale-style gameplay
│   ├── code/            # Game logic and mechanics
│   │   ├── main.py      # Stage 1 entry point
│   │   ├── player.py    # Player character controller
│   │   ├── sprites.py   # Game object classes
│   │   ├── settings.py  # Configuration constants
│   │   └── ...         # Additional game modules
│   ├── audio/          # Sound effects and music
│   ├── data/           # Tilemap and level data
│   └── images/         # Sprites and graphics
└── stage 2/             # Touhou-style bullet hell
    ├── code/           # Game logic and mechanics
    │   ├── main.py     # Stage 2 entry point
    │   ├── sprites.py  # Enemy and bullet classes
    │   ├── support.py  # Asset loading utilities
    │   ├── groups.py   # Sprite group management
    │   └── ...        # Additional game modules
    ├── audio/         # Sound effects and music
    ├── data/          # Tilemap and level data
    └── images/        # Sprites and graphics
```

## 🎯 Gameplay Guide

### Stage 1: Undertale Adventure
**Getting Started:**
- Choose between Story Mode (narrative-focused) or Survival Mode (action-focused)
- Interact with NPCs using Space to learn about game modes
- Story Guide NPC (behind player) introduces philosophical gameplay
- Combat Instructor NPC (left of player) teaches survival mechanics

**Combat System:**
- **ATTACK**: Deal damage to enemies with weapons
- **TALK**: Communicate with enemies, potentially leading to peaceful resolution
- **HEAL**: Restore health when needed
- **SPARE**: Show mercy to enemies after successful dialogue
- **Soul Movement**: During enemy attacks, control a small soul to dodge bullet patterns
- **Blue Bullets**: Only hurt when you're moving - stay still to avoid
- **Orange Bullets**: Only hurt when you're stationary - keep moving to avoid

**Victory Conditions:**
- **Story Mode**: Complete meaningful encounters and choose compassionate paths
- **Survival Mode**: Reach 400 points by defeating enemies
- **Multiple Endings**: Victory, philosophical completion, or determination failure

### Stage 2: Bullet Hell Action
**Core Mechanics:**
- **Precision Movement**: Use WASD/Arrow keys for exact positioning
- **Hitbox Awareness**: Hold Shift to see your tiny collision area (white circle)
- **Enemy Patterns**: Bees fly in straight lines shooting bullet spreads
- **Worms**: Ground-based enemies with different attack patterns
- **Scoring**: Earn points by destroying enemies, bonus points during invulnerability

**Survival Tips:**
- **Focus on dodging** rather than constant shooting
- **Use invulnerability frames** after taking damage to destroy enemies safely
- **Watch for freeze effects** - brief pause after taking damage
- **Track your lives** with the heart display in the top-right corner
- **Aim for high scores** - challenge yourself and others!

## 🔧 Technical Features

### Advanced Game Systems
- **Cross-platform compatibility** with automatic path resolution
- **Custom asset loading** system with fallback options
- **Pixel-perfect collision detection** using pygame masks
- **Dynamic sprite animation** with frame-based systems
- **Integrated audio management** with volume control
- **Sophisticated timer systems** for game events and effects

### Visual & Audio Polish
- **Custom pixel art** sprites and animations
- **Retro-style fonts** with modern fallback support
- **Immersive sound design** including shooting, impacts, and ambient music
- **Visual feedback systems** including damage flashes, freeze effects, and hitbox display
- **Smooth particle effects** and visual polish

### User Experience
- **Comprehensive end screens** with performance statistics
- **Intuitive menu navigation** with keyboard and mouse support
- **Clear visual indicators** for health, score, and game state
- **Responsive controls** with consistent input handling

## 🐛 Troubleshooting

### Common Issues

**Import Errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.7 or higher: `python --version`

**Font Loading Issues:**
- Game automatically falls back to system fonts if custom font fails
- Ensure `fonts/04B_30__.TTF` exists in the project directory

**Audio Problems:**
- Check that audio files exist in respective `stage X/audio/` directories
- Verify system audio is working and unmuted
- Audio will be muted if files are missing (no crash)

**Performance Issues:**
- Close other applications to free up system resources
- Ensure graphics drivers are updated
- Game is optimized for 60 FPS at 1280x720 resolution

**Game Won't Start:**
- Run from the main directory containing `main.py` or `start_screen.py`
- Check console output for specific error messages
- Verify all required files are present (see project structure above)

For additional help, check `TROUBLESHOOTING.md` in the project root.

## 🎮 Development & Credits

**Technical Stack:**
- **Python 3.7+** for cross-platform compatibility
- **pygame-ce** for graphics, audio, and input handling
- **pytmx** for tilemap loading and level design
- **Custom asset pipeline** for efficient resource management

**Game Design Inspiration:**
- **Undertale** by Toby Fox (Stage 1 mechanics and philosophy)
- **Touhou Project** series by ZUN (Stage 2 bullet hell mechanics)
- Classic arcade games for scoring and progression systems

**Development Notes:**
- Built as part of the DPS Saket educational project
- Emphasizes game design principles and programming best practices
- Modular architecture allows for easy expansion and modification

## 📄 License

This project is open source and available under the MIT License. Feel free to explore, learn, and build upon this codebase.

## 🚀 Future Enhancements

Potential areas for expansion:
- **Additional Stages**: More diverse gameplay experiences
- **Boss Battles**: Epic encounters with unique mechanics  
- **Achievement System**: Goals and unlockables for replayability
- **Save System**: Progress persistence and high score tracking
- **Level Editor**: Community-driven content creation
- **Multiplayer**: Cooperative or competitive modes

---

**Ready to embark on your two-stage adventure? Start your journey today! 🎮✨**
