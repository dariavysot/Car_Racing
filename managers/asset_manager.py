"""
Resource management and asset loading system.

Provides a robust interface for loading graphical assets with automatic
procedural fallback generation in case of missing external files.
"""

import os
import pygame as pg
from config import Settings as C


class AssetManager:
    """
    Static utility class for loading and scaling game sprites.

    Contains logic for safe image loading and procedural generation of
    placeholders (fallbacks) for cars, roads, and effects.
    """

    # ----------------------------
    # GENERAL METHODS
    # ----------------------------
    @staticmethod
    def load_sprite(path, fallback_fn):
        """
        Attempt to load an image from disk or trigger a fallback.

        Parameters
        ----------
        path : str
            File system path to the image.
        fallback_fn : callable
            A function that returns a pg.Surface if the file is missing.

        Returns
        -------
        pg.Surface
            The loaded or procedurally generated sprite.
        """
        if os.path.exists(path):
            return pg.image.load(path).convert_alpha()
        return fallback_fn()

    @staticmethod
    def make_car_fallback(color_name):
        """Generate a colored rectangle as a placeholder for a car."""
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
        """Generate a gray surface as a placeholder for the road."""
        surf = pg.Surface((C.WIDTH, 140))
        surf.fill(C.GRAY)
        return surf

    @staticmethod
    def make_explosion_fallback():
        """Generate a gray surface as a placeholder for the road."""
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
        """Load and scale the road texture to fit screen dimensions."""
        img = AssetManager.load_sprite(path, AssetManager.make_road_fallback)
        return pg.transform.smoothscale(img, (C.WIDTH, C.HEIGHT))

    @staticmethod
    def load_car(color_name):
        """Load and scale a player or NPC car sprite by color."""
        path = f"assets/images/{color_name}_car.png"

        img = AssetManager.load_sprite(
            path,
            lambda: AssetManager.make_car_fallback(color_name)
        )

        return pg.transform.smoothscale(img, (C.CAR_WIDTH, C.CAR_HEIGHT))

    @staticmethod
    def load_taxi():
        """Load and scale the taxi obstacle sprite."""
        path = f"assets/images/taxi.png"

        img = AssetManager.load_sprite(
            path,
            lambda: AssetManager.make_car_fallback("yellow")
        )

        return pg.transform.smoothscale(img, (C.CAR_WIDTH, C.CAR_HEIGHT))

    @staticmethod
    def load_truck(num):
        """Load and scale a specific truck sprite."""
        path = f"assets/images/truck_{num}.png"

        img = AssetManager.load_sprite(
            path,
            lambda: AssetManager.make_car_fallback("green")
        )

        return pg.transform.smoothscale(img, (C.CAR_WIDTH, C.TRUCK_HEIGHT))

    @staticmethod
    def load_explosion():
        """Load the explosion animation sprite."""
        path = "assets/images/explosion.png"
        return AssetManager.load_sprite(
            path,
            AssetManager.make_explosion_fallback
        )
