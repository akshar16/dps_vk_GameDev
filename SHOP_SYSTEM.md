# Shop System Implementation

## Overview
A currency-based shop system has been added to Stage 1 where players can earn coins by defeating enemies and spend them on upgrades. **The shop features a modern GUI powered by pygame_gui with a custom dark/gold theme.**

## Features

### Currency System
- **Renamed from Score to Coins**: The existing score system has been converted to a currency system
- **Earning Coins**:
  - Kill enemy with bullets: +1 coin
  - Spare enemy in Undertale battle: +5 coins
  - Defeat enemy in Undertale battle: +3 coins
- **Victory Condition**: Reach 400 coins to win

### Shop NPC
- **Location**: Near the top of the map (X≈1750, Y≈287)
- **Visual**: Animated idle sprite, scaled 3x from original 25x33px to 75x99px
- **Interaction Range**: 100 pixels from the shop sprite

### Shop Items
1. **Health Pack** - 5 coins
   - Restores 5 HP (up to max HP)

2. **Max HP Upgrade** - 10 coins
   - Increases maximum HP by 5
   - Also heals player by 5 HP

3. **Speed Boost** - 8 coins
   - Increases player movement speed by 50 units

4. **Damage Boost** - 12 coins
   - Increases bullet damage by 50% (stacks)

## Controls

### Opening the Shop
- Walk near the Shop NPC (within 100 pixels)
- Press **E** to open the shop GUI window
- UI displays: "Press E to open shop" when nearby

### Shop GUI Navigation
- **Mouse Click**: Click on item buttons to purchase
- **Close Button**: Click the red "Close" button at bottom-right
- **X Button**: Click the window X to close
- **ESC**: Close shop window

### Modern GUI Features
- Professional windowed interface with pygame_gui
- Dark blue theme with gold accents
- Real-time coin balance display at top
- Large, colorful item buttons with descriptions
- Green buttons for affordable items
- Red buttons for items you can't afford
- Smooth hover effects and animations
- Visual feedback on purchase

## UI Elements

### HUD Display
- Top-left corner shows: **"Coins: [amount]"** in gold color (255, 215, 0)
- Near shop: **"Press E to open shop"** appears at bottom center in green

### Shop GUI Window
- Modern windowed interface with pygame_gui library
- Dark navy blue window with gold border
- Title bar: "🛒 SHOP" with window controls
- Top section: **"💰 Your Coins: [amount]"** in large gold text on dark background
- Item grid:
  - 4 large buttons, one per item
  - Button text shows: name, price with coin emoji, and description
  - Green background for affordable items
  - Red background for items you can't afford
  - Cyan/gold borders with hover effects
  - Rounded corners for modern look
- Bottom right: Red "Close" button
- Smooth animations and visual feedback
- Window can be dragged and closed with X button

### Game Over Screen
- Shows **"Final Coins: [amount]"** instead of score

## Technical Implementation

### Dependencies
- **pygame-ce**: Game engine
- **pygame_gui**: Modern UI library for professional-looking interfaces
- **pytmx**: Tiled map loading

### Files Modified
- `stage 1/code/main.py`:
  - Added pygame_gui import and UIManager initialization
  - Created `open_shop_gui()` method to create windowed shop interface
  - Created `close_shop_gui()` method to clean up shop window
  - Modified `purchase_item()` to accept item index and refresh GUI
  - Added pygame_gui event handling (UI_BUTTON_PRESSED, UI_WINDOW_CLOSE)
  - Integrated UI manager updates in main game loop
  - Removed keyboard navigation (arrow keys) in favor of mouse clicks
  - Added check_nearby_shop() proximity detection

- `stage 1/code/sprites.py`:
  - Shop class loads and animates idle frames
  - 3x smoothscale applied to shop sprites
  - Positioned using midbottom anchoring

- `stage 1/code/shop_theme.json`:
  - Custom pygame_gui theme with dark blue/gold color scheme
  - Professional button styling with hover effects
  - Custom fonts and border radius
  - Color-coded buttons (green=affordable, red=too expensive)
  - Themed window decorations

### Key Variables
```python
self.coins = 0                    # Player currency
self.shop_open = False           # Shop menu state
self.nearby_shop = False         # Player in interaction range
self.shop_sprite = Shop(...)     # Reference to Shop NPC sprite

# pygame_gui components
self.ui_manager = UIManager(...)  # pygame_gui manager
self.shop_window = UIWindow(...)  # Main shop window
self.shop_buttons = []            # List of item purchase buttons
self.shop_close_button = UIButton(...) # Close button

self.shop_items = [              # Available items
    {"name": "Health Pack", "price": 5, "description": "Restore 5 HP"},
    {"name": "Max HP Upgrade", "price": 10, "description": "+5 Max HP"},
    {"name": "Speed Boost", "price": 8, "description": "+50 Movement Speed"},
    {"name": "Damage Boost", "price": 12, "description": "Bullets deal more damage"}
]
```

## Gameplay Flow

1. **Exploration Phase**:
   - Player defeats enemies to earn coins
   - Coins counter visible at all times
   - Shop NPC is always visible on the map

2. **Approaching Shop**:
   - When within 100 pixels, "Press E to open shop" appears
   - Shop sprite continues animating

3. **Shopping**:
   - Press E to open GUI window
   - Mouse cursor becomes visible
   - Game pauses (no movement/shooting/enemy attacks)
   - Click item buttons to purchase
   - Window refreshes to show updated coin balance
   - Click "Close" button or ESC to return to game

4. **Item Effects**:
   - Applied immediately upon purchase
   - Health Pack/Max HP: instant healing
   - Speed Boost: permanent movement speed increase
   - Damage Boost: all future bullets deal more damage

## Notes

- **pygame_gui Library**: Provides professional UI components with themes, animations, and mouse interaction
- **Custom Theme**: Dark blue and gold color scheme matches the game's aesthetic
- **Responsive Buttons**: Visual feedback shows which items are affordable vs too expensive
- Shop is far from player spawn (Y=287 vs player Y=1945) - player must travel to reach it
- Shop has no collision - purely visual/interactive
- Multiple purchases stack (e.g., buying Speed Boost twice = +100 speed)
- Victory condition remains at 400 coins (same as old score system)
- Shop window pauses all gameplay including enemy movement and attacks
- GUI can be closed via X button, Close button, or ESC key
- Window is draggable for player convenience
