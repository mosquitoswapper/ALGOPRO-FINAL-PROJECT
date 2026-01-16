#imports
import pygame
import random
from settings import *
from Map import *
from Player import *
from Raycaster import *
from Enemy import Enemy
from game_state import GameState

#Initialisatiob
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
map = Map()
player = Player(map)
clock = pygame.time.Clock()
raycaster = Raycaster(player, map)
# Spawn multiple enemies at tile 
enemies = []
row_count = len(map.grid)
col_count = len(map.grid[0]) #empty space
walkable_tiles = []
for row_index in range(1, row_count - 1):
    for col_index in range(1, col_count - 1):
        if map.grid[row_index][col_index] == 0:
            walkable_tiles.append((row_index, col_index)) #safe space

# Random player and enemy spawns
if walkable_tiles:
    player_row, player_col = random.choice(walkable_tiles)
    player.x = int((player_col + 0.5) * TILESIZE)
    player.y = int((player_row + 0.5) * TILESIZE)


initial_player_x = player.x
initial_player_y = player.y

#safe spawn tiles
ENEMY_COUNT = 4
available_tiles = [t for t in walkable_tiles if t != (player_row, player_col)] if walkable_tiles else []
for (row_index, col_index) in random.sample(available_tiles, k=min(ENEMY_COUNT, len(available_tiles))):
    startX = int((col_index + 0.5) * TILESIZE)
    startY = int((row_index + 0.5) * TILESIZE)
    enemies.append(Enemy(map, startX=startX, startY=startY))

game = GameState()

def reset_game(current_map, walkable):
    new_player = Player(current_map)
    new_player.x = initial_player_x
    new_player.y = initial_player_y
    new_enemies = []

    # Avoid spawning on player tile
    start_row = int(initial_player_y // TILESIZE)
    start_col = int(initial_player_x // TILESIZE)
    spawnable = [t for t in walkable if t != (start_row, start_col)] if walkable else []
    for (row_index, col_index) in random.sample(spawnable, k=min(ENEMY_COUNT, len(spawnable))):
        sx = int((col_index + 0.5) * TILESIZE)
        sy = int((row_index + 0.5) * TILESIZE)
        new_enemies.append(Enemy(current_map, startX=sx, startY=sy))
    new_raycaster = Raycaster(new_player, current_map)
    new_game = GameState()
    return new_player, new_enemies, new_raycaster, new_game

while True:
    
    dt_ms = clock.tick(60)
    dt = dt_ms / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if game.mode != 'play':
                player, enemies, raycaster, game = reset_game(map, walkable_tiles)
        
    # Update during play
    if game.mode == 'play':
        player.update()
        for e in enemies:
            e.update(player)
        raycaster.castAllRays()

    screen.fill((0, 0, 0))

    if game.mode == 'play':
        raycaster.render(screen)
        for enemy in enemies:
            if enemy.canSeePlayer(player.x, player.y):
                enemy.render(screen, player)
        game.trigger_jumpscare_if_close(enemies, player)
    else:
        game.update(dt)
        game.render_overlay(screen)

    pygame.display.update()

pygame.quit()
