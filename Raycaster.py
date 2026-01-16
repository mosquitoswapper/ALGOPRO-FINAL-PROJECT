import pygame
import math
from settings import *
from Ray import *

class Raycaster:
    def __init__(self, player, map):
        self.rays = []
        self.player = player
        self.map = map
        
        self.lightPosition = (player.x, player.y)
        self.lightSize = 250  
        
        self.ceilingColor = (20, 20, 20)  
        self.floorColor = (60, 60, 50)  


    def castAllRays(self):
        self.rays = []
        #start ray at the left
        rayAngle = (self.player.rotationAngle - FOV/2)
        for i in range(NUM_RAYS):
            ray = Ray(rayAngle, self.player, self.map)
            ray.cast()
            self.rays.append(ray)

            rayAngle += FOV / NUM_RAYS
    
    def render(self, screen):
        # follow the player
        self.lightPosition = (self.player.x, self.player.y)

        self.drawFloorCeiling(screen)

        i = 0
        for ray in self.rays:
            # rendering 3d walls over the 2d view
            line_height = (32 / ray.distance) * 415

            draw_begin = (WINDOW_HEIGHT / 2) - (line_height / 2)
            draw_end = line_height

            # light
            distanceToLight = math.sqrt(
                (ray.wall_hit_x - self.lightPosition[0]) ** 2 + 
                (ray.wall_hit_y - self.lightPosition[1]) ** 2
            )
            
            if distanceToLight > self.lightSize:
                lightAmount = 0.15  
            else:
                lightAmount = 0.15 + (0.75 * (1.0 - (distanceToLight / self.lightSize)))
            
            color_value = int(ray.color * lightAmount)

            pygame.draw.rect(screen, (color_value, color_value, color_value), (i*RES, draw_begin, RES, draw_end))
            

            i += 1

    def drawFloorCeiling(self, screen):

        pygame.draw.rect(screen, self.ceilingColor, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT // 2))
        pygame.draw.rect(screen, self.floorColor, (0, WINDOW_HEIGHT // 2, WINDOW_WIDTH, WINDOW_HEIGHT // 2))
