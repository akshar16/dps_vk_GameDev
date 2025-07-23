# Release Notes - DPS Saket Game v1.0.0

## 🎮 Two-Stage Adventure Game - Initial Release

**Release Date:** July 24, 2025  
**Version:** 1.0.0  
**Commit:** da5fa3f

---

## 🌟 What's New

This is the inaugural release of the **DPS Saket Two-Stage Adventure Game**, featuring two distinct gameplay experiences in one cohesive package.

### 🎯 Stage 1: Undertale-Inspired Adventure
- **Story Mode** with interactive NPCs and dialogue system
- **Survival Mode** for endless action
- **Turn-based battle system** with ATTACK/TALK/HEAL/SPARE mechanics
- **Soul-based combat** with blue/orange bullet patterns
- **Multiple endings** based on player choices

### ⚡ Stage 2: Touhou-Style Bullet Hell
- **Fast-paced bullet hell gameplay** with challenging enemy patterns
- **Dynamic enemy spawning** system with bees and worms
- **Score-based progression** with lives system
- **Visual feedback systems** including hitbox display (Shift key)

---

## 🔧 Recent Improvements & Bug Fixes

### Game Over & User Experience Enhancements
- **Enhanced freeze effect** when player takes damage (1-second duration)
- **Improved game over screen timing** - now displays after freeze effect ends
- **Better visual feedback** with freeze overlay (light blue tint)
- **Consistent quit/restart controls** across both stages (ESC to menu, Q to quit)

### Performance & Stability
- **Major folder structure cleanup** - removed problematic spaces from folder names
- **Windows compatibility improvements** - fixed path references and removed problematic files
- **Code optimization** - removed unused classes, variables, and files
- **Bullet spawn balancing** - increased spawn time in Stage 2 to reduce difficulty

### Combat System Refinements
- **Enhanced collision detection** for enemy bullets (red/orange dots)
- **Invulnerability mechanics** with visual indicators (red screen flash)
- **Bonus scoring system** for destroying enemies while invulnerable (+50 points)

---

## 🎮 Controls

### General Controls
- **Arrow Keys/WASD:** Move player
- **Mouse:** Aim and shoot (Stage 1)
- **Shift:** Show hitbox (Stage 2)
- **Space:** Interact with NPCs, confirm selections
- **ESC:** Return to menu (game over screens)
- **Q:** Quit game (game over screens)

### Undertale Battles (Stage 1)
- **Arrow Keys/WASD:** Navigate menus and move soul
- **Space/Enter:** Confirm selection
- **Left/Right:** Select battle options

---

## 📋 System Requirements

- **Python 3.x** (tested with 3.13)
- **pygame-ce 2.5.5**
- **pytmx** for tilemap support
- **macOS/Windows/Linux** compatible

---

## 🎯 Key Features

### Visual & Audio
- **Custom pixel art graphics** with multiple character sprites
- **Immersive sound effects** for shooting, impacts, and background music
- **Heart-based life system** with visual indicators
- **Smooth animations** and particle effects

### Gameplay Mechanics
- **Dual-stage progression** system
- **Multiple enemy types** with unique behaviors
- **Dynamic difficulty scaling**
- **Score tracking and performance metrics**

---

## 🐛 Known Issues

- None reported in this release

---

## 📖 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akshar16/dps_saket.git
   cd dps_saket
   ```

2. Install dependencies:
   ```bash
   pip install pygame-ce pytmx
   ```

3. Run the game:
   ```bash
   python main.py
   ```

---

## 🚀 What's Next

Future updates may include:
- Additional stages and levels
- Boss battles and special encounters
- Achievement system
- Customizable controls
- Save/load functionality

---

## 🙏 Acknowledgments

Developed as part of the DPS Saket project, combining classic game mechanics with modern Python development practices.

---

**Enjoy the adventure! 🎮✨**
