"""
Road environment module.

Handles the background rendering and the infinite scrolling logic to 
simulate continuous vehicle movement.
"""

from config import Settings as C

class Road:
    """
    Manager for the scrolling road background.

    Uses a dual-surface technique to create a seamless infinite loop, 
    moving textures vertically based on the current game speed.

    Attributes
    ----------
    image : pg.Surface
        The texture used for the road background.
    y1 : float
        Vertical position of the first road segment.
    y2 : float
        Vertical position of the second road segment (initially off-screen).
    """
    def __init__(self, image):
        """
        Initialize the Road with a background texture.

        Parameters
        ----------
        image : pg.Surface
            The background image to be looped.
        """
        self.image = image
        self.y1 = 0
        self.y2 = -C.HEIGHT

    def update(self, dt_sec, speed):
        """
        Update the vertical positions of road segments.

        Calculates movement based on delta time and speed, resetting segment 
        positions once they move completely off-screen to ensure a seamless loop.

        Parameters
        ----------
        dt_sec : float
            Delta time in seconds since the last frame.
        speed : float
            Current movement speed in pixels per second.
        """
        dy = speed * dt_sec

        self.y1 += dy
        self.y2 += dy

        if self.y1 >= C.HEIGHT:
            self.y1 = self.y2 - C.HEIGHT
        if self.y2 >= C.HEIGHT:
            self.y2 = self.y1 - C.HEIGHT

    def draw(self, screen):
        """
        Render both road segments to the screen.

        Parameters
        ----------
        screen : pg.Surface
            The target surface for rendering.
        """
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))
