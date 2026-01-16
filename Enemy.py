import math
import random
import pygame
from settings import *

class Enemy:

    def __init__(self, map, startX, startY):
        self.map = map

        self.x = startX
        self.y = startY
        self.radius = 8
        self.speed = 1.2
        self.angle = 0.0
        
        try:
            self.sprite = pygame.image.load(ENEMY_SPRITE_PATH).convert_alpha()
        except Exception:
            self.sprite = None

        self.state = 'WALK'
        self.target = None  
        self.visionRange = TILESIZE * 8

    def canSeePlayer(self, playerX, playerY):
        dx = playerX - self.x
        dy = playerY - self.y
        distance_to_player = math.hypot(dx, dy)
        if distance_to_player > self.visionRange:
            return False
        if distance_to_player < 0.00001:
            return True

        
        angle_to_player = math.atan2(dy, dx)

        is_facing_down = angle_to_player > 0 and angle_to_player < math.pi
        is_facing_up = not is_facing_down
        is_facing_right = angle_to_player < 0.5 * math.pi or angle_to_player > 1.5 * math.pi
        is_facing_left = not is_facing_right

        # Horizon check
        found_horizontal_wall = False
        horizontal_hit_x = 0
        horizontal_hit_y = 0

        # finding ys
        if is_facing_up:
            first_intersection_y = ((self.y // TILESIZE) * TILESIZE) - 0.01
        elif is_facing_down:
            first_intersection_y = ((self.y // TILESIZE) * TILESIZE) + TILESIZE
        
        # finding x 
        if abs(math.sin(angle_to_player)) < 0.0001:  
            first_intersection_x = self.x
        else:
            first_intersection_x = self.x + (first_intersection_y - self.y) / math.tan(angle_to_player)

        nextHorizontalX = first_intersection_x
        nextHorizontalY = first_intersection_y

        xa = 0
        ya = 0

        # 1. Finding Ya
        if is_facing_up:
            ya = -TILESIZE
        elif is_facing_down:
            ya = TILESIZE
        
        # 2. Finding Xa (guard against vertical angle)
        if abs(math.sin(angle_to_player)) < 0.0001: 
            xa = 0
        else:
            xa = ya / math.tan(angle_to_player)

        # windows
        while (nextHorizontalX <= WINDOW_WIDTH and nextHorizontalX >= 0 and nextHorizontalY <= WINDOW_HEIGHT and nextHorizontalY >= 0):
            if self.map.has_wall_at(nextHorizontalX, nextHorizontalY):
                found_horizontal_wall = True
                horizontal_hit_x = nextHorizontalX
                horizontal_hit_y = nextHorizontalY
                break
            else:
                nextHorizontalX += xa
                nextHorizontalY += ya

        # Vert check
        found_vertical_wall = False
        vertical_hit_x = 0
        vertical_hit_y = 0

        if is_facing_right:
            first_intersection_x = ((self.x // TILESIZE) * TILESIZE) + TILESIZE
        elif is_facing_left:
            first_intersection_x = ((self.x // TILESIZE) * TILESIZE) - 0.01
        
        # finding y (guard against horizontal angle)
        if abs(math.cos(angle_to_player)) < 0.0001:  # nearly horizontal
            first_intersection_y = self.y
        else:
            first_intersection_y = self.y + (first_intersection_x - self.x) * math.tan(angle_to_player)
        
        nextVerticalX = first_intersection_x
        nextVerticalY = first_intersection_y

        # 1. xa
        if is_facing_right:
            xa = TILESIZE
        elif is_facing_left:
            xa = -TILESIZE
        
        # finding ya (guard against horizontal angle)
        if abs(math.cos(angle_to_player)) < 0.0001:  # nearly horizontal
            ya = 0
        else:
            ya = xa * math.tan(angle_to_player)

        while (nextVerticalX <= WINDOW_WIDTH and nextVerticalX >= 0 and nextVerticalY <= WINDOW_HEIGHT and nextVerticalY >= 0):
            if self.map.has_wall_at(nextVerticalX, nextVerticalY):
                found_vertical_wall = True
                vertical_hit_x = nextVerticalX
                vertical_hit_y = nextVerticalY
                break
            else:
                nextVerticalX += xa
                nextVerticalY += ya

        # Distance
        horizontal_distance = 0
        vertical_distance = 0

        if found_horizontal_wall:
            horizontal_distance = math.hypot(horizontal_hit_x - self.x, horizontal_hit_y - self.y)
        else:
            horizontal_distance = 999
        if found_vertical_wall:
            vertical_distance = math.hypot(vertical_hit_x - self.x, vertical_hit_y - self.y)
        else:
            vertical_distance = 999
        nearest_wall_distance = min(horizontal_distance, vertical_distance)

        
        return nearest_wall_distance >= distance_to_player

    def moveTowards(self, tx, ty):
        angle = math.atan2(ty - self.y, tx - self.x)
        step_x = math.cos(angle) * self.speed
        step_y = math.sin(angle) * self.speed
        pad = self.radius

        # move x and y
        new_x = self.x + step_x
        if not (self.map.has_wall_at(new_x + pad, self.y) or
                self.map.has_wall_at(new_x - pad, self.y) or
                self.map.has_wall_at(new_x, self.y + pad) or
                self.map.has_wall_at(new_x, self.y - pad)):
            self.x = new_x

        new_y = self.y + step_y
        if not (self.map.has_wall_at(self.x, new_y + pad) or
                self.map.has_wall_at(self.x, new_y - pad) or
                self.map.has_wall_at(self.x + pad, new_y) or
                self.map.has_wall_at(self.x - pad, new_y)):
            self.y = new_y

        self.angle = angle

    def wandertargt(self):
        # dif path
        tx = self.x + random.choice([-1, 0, 1]) * TILESIZE
        ty = self.y + random.choice([-1, 0, 1]) * TILESIZE
        tx = (int(tx // TILESIZE) + 0.5) * TILESIZE
        ty = (int(ty // TILESIZE) + 0.5) * TILESIZE
        self.target = None if self.map.has_wall_at(tx, ty) else (tx, ty)

    def update(self, player):
        if self.canSeePlayer(player.x, player.y):
            self.state = 'CHASING'
            self.target = (player.x, player.y)
        else:
            if self.state != 'WALK' or self.target is None:
                self.state = 'WALK'
                self.wandertargt()

        if not self.target:
            return

        tx, ty = self.target
        if math.hypot(tx - self.x, ty - self.y) < 6.0:
            if self.state == 'WALK':
                self.wandertargt()
            else:
                self.target = (player.x, player.y)
        else:
            # add speed when chasing
            if self.state == 'CHASING':
                old = self.speed
                self.speed = old * 1.2
                self.moveTowards(tx, ty)
                self.speed = old
            else:
                self.moveTowards(tx, ty)

    def render(self, screen, player):
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)
        if distance < 0.00001:
            return

        player_to_enemy = math.atan2(dy, dx)
        angle_difference = normalize_angle(player_to_enemy - player.rotationAngle + math.pi) - math.pi
        if abs(angle_difference) > FOV / 2:
            return

        window_width = int((angle_difference / FOV + 0.5) * WINDOW_WIDTH)

        scale = max(0.1, min(2.0, (TILESIZE / max(8.0, distance)) * 1.8))
        height = int(48 * scale)

        draw_y = WINDOW_HEIGHT // 2 + TILESIZE // 4
        draw_x = window_width

        if self.sprite:
            spr_w, spr_h = self.sprite.get_size()
            target_h = max(10, int(height))
            target_w = max(10, int(spr_w * (target_h / spr_h)))
            sprite_scaled = pygame.transform.smoothscale(self.sprite, (target_w, target_h))
            sprite_rect = sprite_scaled.get_rect()
            sprite_rect.center = (draw_x, draw_y)
            screen.blit(sprite_scaled, sprite_rect)


def normalize_angle(angle):
    angle = angle % (2 * math.pi)
    if angle <= 0:
        angle = (2 * math.pi) + angle
    return angle
