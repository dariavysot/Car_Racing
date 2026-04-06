"""
Base module for game entities.

This module defines the `GameObject` class, which serves as the foundational
class for all renderable and movable objects in the game. It provides
standardized methods for sprite rendering and dynamic lighting effects.
"""

import pygame as pg
from config import Settings as C


class GameObject:
    """
    Base class for drawable game entities.

    Provides a unified interface for sprite positioning, basic rendering,
    and advanced light-mask generation for night mode.

    Attributes
    ----------
    image : pg.Surface
        The visual representation (sprite) of the object.
    rect : pg.Rect
        The bounding box used for positioning and collision detection.
    """

    def __init__(self, image, x, y):
        """
        Initialize the GameObject.

        Parameters
        ----------
        image : pg.Surface
            The sprite surface for the object.
        x : int
            Initial horizontal center position.
        y : int
            Initial vertical center position.
        """
        self.image = image
        self.rect = image.get_rect(center=(x, y))

    def update(self, *args, **kwargs):
        """Update object state. Intended to be overridden in subclasses."""
        pass

    def draw(self, screen):
        """
        Render the object's sprite to the screen.

        Parameters
        ----------
        screen : pg.Surface
            The target surface for rendering.
        """
        screen.blit(self.image, self.rect)

    def draw_lights(self, screen, is_night, direction="SAME"):
        """
        Coordinate the rendering of both front and rear lighting.

        This method acts as a high-level controller for the object's emissive
        effects during night mode.

        Parameters
        ----------
        screen : pg.Surface
            The target surface for blitting light effects.
        is_night : bool
            Activation flag. If False, rendering is skipped.
        direction : str, optional
            The travel direction ("SAME" or "OPPOSITE") used to orient
            the light cones. Defaults to "SAME".
        """
        if not is_night:
            return

        self._draw_headlights(screen, direction)
        self._draw_taillights(screen, direction)

    def _draw_headlights(self, screen, direction):
        """
        Render the gradient headlight cones.

        Generates a semi-transparent trapezoidal surface with a quadratic
        alpha fade to simulate realistic light dispersion.

        Parameters
        ----------
        screen : pg.Surface
            The surface where headlights will be blitted.
        direction : str
            Determines whether lights point up or down and their
            relative offset from the vehicle's body.
        """
        top_width = int(self.rect.width * C.LIGHT_TOP_WIDTH_FACTOR)
        bottom_width = int(self.rect.width * C.LIGHT_BOTTOM_WIDTH_FACTOR)

        light_surf = pg.Surface((bottom_width, C.LIGHT_HEIGHT), pg.SRCALPHA)
        center_x = bottom_width // 2

        for y in range(C.LIGHT_HEIGHT):
            progress = y / C.LIGHT_HEIGHT

            alpha = int(C.NIGHT_ALPHA * (1 - progress) ** 1.5)
            current_width = top_width + (bottom_width - top_width) * progress

            pg.draw.line(
                light_surf,
                (*C.LIGHT_COLOR, alpha),
                (int(center_x - current_width / 2), C.LIGHT_HEIGHT - y),
                (int(center_x + current_width / 2), C.LIGHT_HEIGHT - y)
            )

        pos_x = self.rect.centerx - bottom_width // 2

        if direction == "OPPOSITE":
            flipped_light = pg.transform.flip(light_surf, False, True)
            # Light comes from the bottom of the car
            pos_y = self.rect.bottom - 5
            screen.blit(flipped_light, (pos_x, pos_y))
        else:
            # Light comes from the top of the car
            pos_y = self.rect.top - C.LIGHT_HEIGHT + 5
            screen.blit(light_surf, (pos_x, pos_y))

    def _draw_taillights(self, screen, direction):
        """
        Render the rear emissive red lights and their associated glow.

        Draws fixed-position circles and applies an additive bloom effect
        using a separate alpha surface.

        Parameters
        ----------
        screen : pg.Surface
            The surface where taillights will be blitted.
        direction : str
            Determines the vertical positioning of the lights (top/bottom
            of the rect) to match the car's orientation.
        """
        back_y = self.rect.top + 3 if direction == "OPPOSITE" else self.rect.bottom - 3

        dot_radius = C.TAIL_LIGHT_DOT_RADIUS
        glow_radius = C.TAIL_LIGHT_GLOW_RADIUS

        for offset in [-self.rect.width // 3.5, self.rect.width // 3.5]:
            pos = (int(self.rect.centerx + offset), int(back_y))

            pg.draw.circle(screen, C.TAIL_LIGHT_COLOR, pos, dot_radius)

            glow_surf = pg.Surface(
                (glow_radius * 2, glow_radius * 2), pg.SRCALPHA)
            pg.draw.circle(glow_surf, (200, 0, 0, 30),
                           (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf,
                        (pos[0] - glow_radius, pos[1] - glow_radius),
                        special_flags=pg.BLEND_RGB_ADD)
