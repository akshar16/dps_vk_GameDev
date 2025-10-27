import pygame 
from os.path import join 
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720 
TILE_SIZE = 64

# Vertical nudge for Shop NPC anchoring (negative lifts up)
SHOP_Y_OFFSET = -64