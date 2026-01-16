import math
TILESIZE = 32 #Each tile is 32x32 pixels

ROWS = 20
COLS = 25

WINDOW_WIDTH = COLS * TILESIZE
WINDOW_HEIGHT = ROWS * TILESIZE

FOV = 60 * (math.pi / 180)  # Convert degrees to radians

#Defining resolution
RES = 2

#Number of rays for raycasting
NUM_RAYS = WINDOW_WIDTH // RES


ENEMY_SPRITE_PATH = "Employment-Job-Application-791x1024.webp"


