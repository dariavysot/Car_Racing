"""
Environmental theme and lighting management.

This module defines the `ThemeManager` class, which handles periodic
transitions between day and night modes using full-screen alpha overlays.
"""

import pygame as pg
from config import Settings as C


class ThemeManager:
    """
    Controller for environmental lighting cycles.

    Manages a timer-based system that toggles the game's visual state
    between daylight and night mode, providing a dark surface mask
    for light-source pass rendering.

    Attributes
    ----------
    is_night : bool
        Current lighting state of the environment.
    timer : float
        Elapsed time since the last theme transition.
    interval : int
        Duration in milliseconds between theme toggles.
    dark_overlay : pg.Surface
        A semi-transparent black surface used as a darkness mask.
    """

    def __init__(self):
        """
        Initialize the ThemeManager.

        Sets up the timing intervals and pre-renders the darkness overlay
        surface with the transparency levels defined in the configuration.
        """
        self.is_night = False
        self.timer = 0
        self.interval = C.THEME_INTERVAL

        self.dark_overlay = pg.Surface((C.WIDTH, C.HEIGHT))
        self.dark_overlay.fill((0, 0, 0))
        self.dark_overlay.set_alpha(C.NIGHT_ALPHA)

    def reset(self):
        """
        Reset the manager to default daylight state.

        Should be called whenever a new game session starts to ensure
        consistency in the initial lighting.
        """
        self.is_night = False
        self.timer = 0

    def update(self, dt):
        """
        Update the internal timer and trigger state transitions.

        Parameters
        ----------
        dt : int
            Delta time in milliseconds since the last frame.
        """
        self.timer += dt
        if self.timer >= self.interval:
            self.toggle()
            self.timer = 0

    def toggle(self):
        """Switch the current lighting state between Day and Night."""
        self.is_night = not self.is_night

    def apply(self, screen):
        """
        Apply the darkness mask to the screen surface.

        Parameters
        ----------
        screen : pg.Surface
            The target surface (usually the main game screen) to darken.
        """
        if self.is_night:
            screen.blit(self.dark_overlay, (0, 0))
