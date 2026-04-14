
from config import Settings as C
from core.game_object import GameObject



class Obstacle(GameObject):
    """
    A class representing an obstacle in the game world.

    Obstacles are spawned on specific lanes and move downwards at a constant
    speed. Inherits from the base GameObject class.

    Parameters
    ----------
    image : pg.Surface
        The visual representation (texture) of the obstacle.
    lane : int
        The index of the lane where the obstacle is positioned (0, 1, 2...).
    y : int or float
        The initial vertical coordinate.
    speed : int or float
        The vertical movement speed in pixels per second.

    Attributes
    ----------
    lane : int
        The current lane index of the obstacle.
    speed : float
        The speed at which the obstacle moves downward.
    rect : pg.Rect
        The rectangular area defining the position and size (inherited).
    """

    def __init__(self, image, lane, y, speed, direction="SAME"):
        self.lane = lane
        self.speed = speed
        self.direction = direction
        x = C.LANE_WIDTH * lane + C.LANE_OFFSET
        super().__init__(image, x, y)

    def update(self, dt_sec):
        """
        Update the obstacle's state by moving it down the screen.

        Parameters
        ----------
        dt_sec : float
            The time elapsed since the last frame in seconds (delta time).
        """
        self.rect.y += self.speed * dt_sec

    def is_out(self):
        """
        Check if the obstacle has moved completely off the bottom of the screen.

        Returns
        -------
        bool
            True if the obstacle is out of bounds, False otherwise.
        """
        return self.rect.y >= C.HEIGHT + C.CAR_HEIGHT + C.LIGHT_HEIGHT

    def collides(self, player_rect):
        """
        Determine if the obstacle's bounding box intersects with the player's.

        Parameters
        ----------
        player_rect : pg.Rect
            The rectangle representing the player's car hitbox.

        Returns
        -------
        bool
            True if a collision is detected, False otherwise.
        """
        return self.rect.colliderect(player_rect)

    def draw(self, screen):
        """
        Render the obstacle's body.

        Parameters
        ----------
        screen : pg.Surface
            Target surface for rendering.
        """
        super().draw(screen)

    def draw_only_light(self, screen, is_night):
        """
        Render only the lighting effects for the obstacle.

        This is used in the multi-pass rendering pipeline after the
        darkness overlay is applied.

        Parameters
        ----------
        screen : pg.Surface
            Target surface for rendering.
        is_night : bool
            Activation flag for night mode effects.
        """
        self.draw_lights(screen, is_night, self.direction)
