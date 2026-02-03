import os
import pygame as pg
from config import Settings as C

class AssetManager:
    @staticmethod
    def load_sprite(path, fallback_fn):
        if os.path.exists(path):
            return pg.image.load(path).convert_alpha()
        return fallback_fn()

    @staticmethod
    def make_car_fallback(color):
        surf = pg.Surface((60, 10), pg.SRCALPHA)
        pg.draw.rect(surf, color, surf.get_rect(), border_radius=10)
        return surf

    @staticmethod
    def make_road_fallback():
        surf = pg.Surface((C.WIDTH, 140))
        surf.fill(C.GRAY)
        return surf

    @staticmethod
    def make_explosion_fallback():
        radius = 50
        surf = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
        pg.draw.circle(surf, C.YELLOW, (radius, radius), radius)
        pg.draw.circle(surf, C.RED, (radius, radius), radius - 10)
        return surf