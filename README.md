# DPS Saket Game – Survivor: Memory & Invisibility

Fast TL;DR to run, build, and ship. Full details follow below.

Quick start
- Run locally: see "Installation & Setup" below, then python start_screen.py
- Web/itch.io: build with pygbag and upload; see ITCH_UPLOAD.md
- macOS app: use scripts/build_macos.sh (creates builds/dps_saket-macos.zip)
- Controls: ↑↓ navigate, Enter/Space select, Esc back; stage-specific controls below

A Python-based two-stage game built with pygame-ce, featuring custom pixel art, audio, and two distinct modes: a flashlight survival challenge (Stage 1) and a memory-sequencing shooter (Stage 2).

## 🎮 Game Overview

### Stage 1: Nightfall Survival
- Flashlight gameplay: enemies freeze inside the light, hunt in the dark
- Explore, earn coins, visit shop; survival-only flow (reach 400 coins to win)
- Darkness overlay with realistic cone, minimap pings, and “ghost” memory trails
- Freeze effect on damage and responsive enemy AI

### Stage 2: Memory Sequence
- Simon-says style sequence with moving bees: memorize the order during SHOW phase
- Shoot bees in the exact order during INPUT; wrong shot restarts the level
- Memory Flash (E) temporarily reveals everything; drains a meter that refills on level clears
- Shift shows a small precise hitbox; worms persist as extra hazards

## 🎯 Controls

### Universal Controls
- Arrow Keys/WASD: Move
- ESC: Back to menu (from game over screens)
- Q: Quit (from game over screens)

### Stage 1 (Nightfall Survival)
- Mouse: Aim flashlight and shoot
- Left Click: Fire
- Enter: Start survival mode

### Stage 2 (Memory Sequence)
- Mouse: Aim and shoot targets
- Left Click: Shoot
- E: Toggle Memory Flash (drains meter while active)
- Left Shift: Show precise hitbox

## 📋 System Requirements

- Python: 3.10+ recommended (tested with 3.13)
- Dependencies: pygame-ce >= 2.5.0, pytmx >= 3.21.7, pygame_gui >= 0.6.9
- Platforms: Windows, macOS, Linux
- Audio device recommended for music/effects

## 🚀 Installation & Setup

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/akshar16/isdps_vk_GameDev.git
   cd isdps_vk_GameDev
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

Tip: main.py just calls start_screen.main(); running either is fine.

## 📁 Project Structure

```
isdps_vk_GameDev/
├── main.py                 # Game launcher (calls start_screen)
├── start_screen.py         # Main menu and stage selection
├── requirements.txt        # Python dependencies
├── ITCH_UPLOAD.md          # How to build/upload web & macOS
├── scripts/                # Build and upload helpers
│   ├── build_macos.sh      # PyInstaller macOS app
│   └── build_web.sh        # pygbag HTML5 build
├── builds/                 # Output zips (ignored in CI releases)
├── TROUBLESHOOTING.md      # Common issues and solutions
├── fonts/                  # Custom game fonts
├── hearts/                 # UI elements
├── stage 1/                # Stage 1 content and code
└── stage 2/                # Stage 2 content and code
```

## 🚢 Build and publish (itch.io)

- Web (HTML5): build with pygbag and upload the zip as a “played in browser” file. Set index.html as primary, viewport 1280×720.
- macOS: build the .app zip with the script and upload as a downloadable.

See ITCH_UPLOAD.md for the exact steps, commands, and troubleshooting.

## 🎯 Gameplay Guide

### Stage 1: Nightfall Survival
Getting started:
- Press Enter to start Survival Only mode
- Use your flashlight cone to freeze enemies, then shoot them safely
- Collect coins; reach 400 coins to win

Tips:
- Sweep the light in arcs to control space
- Back up when enemies approach from the dark
- Use the minimap and fading “ghost” markers to remember enemy locations

### Stage 2: Memory Sequence
Core loop:
- SPAWNING: Bees enter the arena and move into formation
- SHOW: Bees highlight one-by-one in a random order — memorize it
- INPUT: Shoot the bees in that exact order
- Next level: Order length or count increases; worms respawn as hazards

Tips:
- Use E to briefly reveal everything, but manage the meter
- Shift to see your precise hitbox for tight dodges
- A wrong shot restarts the current level — take your time

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
