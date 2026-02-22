import math
import pygame as pg

class GameState:
    def __init__(self):
        self.time = 0
        self.speed = 4.0
        self.max_enemies = 0.2
        self.spawn_interval = 1800
        self.last_spawn = pg.time.get_ticks()

    def reset(self):
        self.__init__()

    def update_difficulty(self):
        self.speed = 4.0 + math.log(self.time + 1, 4)
        self.max_enemies = min(max(0.2, (self.time + 20) / 100), 0.6)
        self.spawn_interval = max(1400, 1800 - 10 * self.time)