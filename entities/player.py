"""
Player car entity module.

Defines the `PlayerCar` class, which handles user-controlled vehicle 
movement, input processing, and screen boundary constraints.
"""

import pygame as pg
from config import Settings as C
from core.game_object import GameObject

class PlayerCar(GameObject):
    """
    Represents the user-controlled racing car.

    Inherits from `GameObject` and implements horizontal movement 
    logic based on configurable keyboard input.

    Attributes
    ----------
    speed : int
        Horizontal movement speed in pixels per frame.
    left_key : int
        Pygame key constant for moving left.
    right_key : int
        Pygame key constant for moving right.
    direction : int
        Current movement state (-1 for left, 1 for right, 0 for idle).
    """

    def __init__(self, image, left_key=pg.K_LEFT, right_key=pg.K_RIGHT):
        """
        Initialize the PlayerCar with specific controls.

        Parameters
        ----------
        image : pg.Surface
            The sprite surface for the player car.
        left_key : int, optional
            Key for left movement. Defaults to pg.K_LEFT.
        right_key : int, optional
            Key for right movement. Defaults to pg.K_RIGHT.
        """
        start_x = C.WIDTH // 2
        start_y = C.PLAYER_Y

        super().__init__(image, start_x, start_y)
        self.speed = C.PLAYER_LANE_SPEED
        self.left_key = left_key
        self.right_key = right_key
        self.direction = 0

    def update(self, keys, dt_sec):
        """
        Process input and update the car's horizontal position.

        Ensures the car stays within the horizontal bounds of the screen.

        Parameters
        ----------
        keys : pygame.key.ScancodeWrapper
            The current state of all keyboard buttons.
        """
        self.direction = 0

        if keys[self.left_key]:
            self.rect.x -= self.speed * dt_sec
            self.direction = -1

        if keys[self.right_key]:
            self.rect.x += self.speed * dt_sec
            self.direction = 1

        self.rect.x = max(0, min(self.rect.x, C.WIDTH - self.rect.width))

    def draw(self, screen):
        """
        Render the player car body.

        Parameters
        ----------
        screen : pg.Surface
            Target surface for rendering.
        """
        super().draw(screen)

    def draw_only_light(self, screen, is_night):
        """
        Render only the player car's lighting effects.

        Implemented as part of the multi-pass rendering pipeline.

        Parameters
        ----------
        screen : pg.Surface
            Target surface for rendering.
        is_night : bool
            Activation flag for night mode effects.
        """
        self.draw_lights(screen, is_night, direction="SAME")
