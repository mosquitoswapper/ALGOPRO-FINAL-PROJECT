import math
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, TILESIZE

class GameState:
    def __init__(self):
        self.mode = 'play'  
        self.fade_timer = 0.0

    def trigger_jumpscare_if_close(self, enemies, player):
        if self.mode != 'play':
            return
        for e in enemies: #checking enemy dustance
            dist = math.hypot(e.x - player.x, e.y - player.y)
            if dist < TILESIZE * 0.9:
                self.mode = 'dead'
                self.fade_timer = 0.0
                break
    #update each screeb
    def update(self, dt: float):
        # dt is seconds elapsed since last frame
        if self.mode == 'dead':
            self.fade_timer += dt

    def render_overlay(self, screen):
        if self.mode == 'dead':
            screen.fill((0, 0, 0))
            if self.fade_timer >= 0.5:
                font = pygame.font.SysFont(None, 96)
                text = font.render("u ded", True, (230, 230, 230))
                trect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
                screen.blit(text, trect)
                hint_font = pygame.font.SysFont(None, 36)
                hint = hint_font.render("press R to restart", True, (200, 200, 200))
                hrect = hint.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 30))
                screen.blit(hint, hrect)
