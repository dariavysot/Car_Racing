import math
import pygame as pg

def calculate_speed(time):
    base = 240
    return base + math.log(time + 1, 4) * 60

class GameState:
    def __init__(self):
        self.time = 0
        self.speed = 4.0
        self.max_enemies = 0.2
        self.spawn_interval = 1800
        self.last_spawn = pg.time.get_ticks()
        self.paused = False

    def reset(self):
        self.__init__()

    def update(self, dt_sec):
        self.time += dt_sec
        self.speed = calculate_speed(self.time)
        self.max_enemies = min(max(0.34, (self.time + 20) / 100), 0.67)
        self.spawn_interval = max(1400, 1800 - 10 * self.time)