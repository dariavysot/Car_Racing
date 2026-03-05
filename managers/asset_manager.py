import os
import pygame as pg
from config import Settings as C

class AssetManager:
    # ----------------------------
    # GENERAL METHODS
    # ----------------------------
    @staticmethod
    def load_sprite(path, fallback_fn):
        if os.path.exists(path):
            return pg.image.load(path).convert_alpha()
        return fallback_fn()

    @staticmethod
    def make_car_fallback(color_name):
        color_map = {
            "red": C.RED,
            "blue": C.BLUE,
            "yellow": C.YELLOW,
            "purple": C.PURPLE,
            "green": C.GREEN,
            "orange": C.ORANGE,
        }
        color = color_map.get(color_name, C.RED)
        surf = pg.Surface((C.CAR_WIDTH, C.CAR_HEIGHT), pg.SRCALPHA)
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

    # ----------------------------
    # LOGIN.PY WRAPS
    # ----------------------------
    @staticmethod
    def load_road(path="assets/images/road.png"):
        img = AssetManager.load_sprite(path, AssetManager.make_road_fallback)
        return pg.transform.smoothscale(img, (C.WIDTH, C.HEIGHT))

    @staticmethod
    def load_car(color_name):
        path = f"assets/images/{color_name}_car.png"

        img = AssetManager.load_sprite(
            path,
            lambda: AssetManager.make_car_fallback(color_name)
        )

        return pg.transform.smoothscale(img, (C.CAR_WIDTH, C.CAR_HEIGHT))

    @staticmethod
    def load_taxi():
        path = f"assets/images/taxi.png"

        img = AssetManager.load_sprite(
            path,
            lambda: AssetManager.make_car_fallback("yellow")
        )

        return pg.transform.smoothscale(img, (C.CAR_WIDTH, C.CAR_HEIGHT))

    @staticmethod
    def load_truck(num):
        path = f"assets/images/truck_{num}.png"

        img = AssetManager.load_sprite(
            path,
            lambda: AssetManager.make_car_fallback("green")
        )

        return pg.transform.smoothscale(img, (C.CAR_WIDTH, C.TRUCK_HEIGHT))

    @staticmethod
    def load_explosion():
        return AssetManager.load_sprite("assets/images/explosion.png", AssetManager.make_explosion_fallback)
