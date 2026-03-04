import pygame as pg
from config import Settings as C


class ThemeManager:
    def __init__(self):
        self.is_night = False
        self.timer = 0
        self.interval = C.THEME_INTERVAL

        self.dark_overlay = pg.Surface((C.WIDTH, C.HEIGHT))
        self.dark_overlay.fill((0, 0, 0))
        self.dark_overlay.set_alpha(C.NIGHT_ALPHA)

    def reset(self):
        self.is_night = False
        self.timer = 0

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