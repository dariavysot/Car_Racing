import math
import pygame as pg

def calculate_speed(time, base=240):
    """
    Calculate the game speed based on elapsed time using logarithmic scaling.

    Parameters
    ----------
    time : float
        The total elapsed game time in seconds.

    Returns
    -------
    float
        The calculated speed value.

    Notes
    -----
    The speed follows the formula:
    base + log{4}(time + 1) * 60
    """
    return base + math.log(time + 1, 4) * 60

class GameState:
    """
    A class to manage the global state and difficulty scaling of the game.

    This class tracks time, movement speed, enemy density, and spawning 
    logic. It scales difficulty dynamically as the game progresses.

    Attributes
    ----------
    time : float
        Total time elapsed since the start of the game session in seconds.
    speed : float
        Current movement speed for game objects.
    max_enemies : float
        A factor representing the maximum allowed enemy density.
    spawn_interval : int or float
        The time delay between enemy spawns in milliseconds.
    last_spawn : int
        The timestamp (in ms) of the last successful enemy spawn.
    paused : bool
        Flag indicating whether the game logic is currently paused.
    """

    def __init__(self, base=240):
        self.time = 0
        self.base = base
        self.speed = self.base
        self.max_enemies = 0.2
        self.spawn_interval = 1800
        self.last_spawn = pg.time.get_ticks()
        self.paused = False
        self.started = False

    def reset(self):
        """
        Reset the game state to its initial default values.
        """
        self.__init__()

    def update(self, dt_sec):
        """
        Update game metrics and difficulty scaling based on elapsed time.

        Parameters
        ----------
        dt_sec : float
            The time elapsed since the last frame in seconds (delta time).
        """
        self.time += dt_sec
        self.speed = calculate_speed(self.time, base=self.base)
        self.max_enemies = min(max(0.34, (self.time + 20) / 100), 0.67)
        self.spawn_interval = max(1400, 1800 - 10 * self.time)