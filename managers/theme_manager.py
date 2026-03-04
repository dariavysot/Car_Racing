import pygame as pg
from config import Settings as C


class ThemeManager:
    def __init__(self):
        self.is_night = False
        self.timer = 0
        self.interval = 2000

        self.dark_overlay = pg.Surface((C.WIDTH, C.HEIGHT))
        self.dark_overlay.fill((0, 0, 0))
        self.dark_overlay.set_alpha(120)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.toggle()
            self.timer = 0

    def toggle(self):
        self.is_night = not self.is_night

    def apply(self, screen):
        if self.is_night:
            screen.blit(self.dark_overlay, (0, 0))