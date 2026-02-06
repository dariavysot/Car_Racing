import pygame as pg

class GameState:
    def __init__(self):
        self.score = 0
        self.difficulty = 1.0
        self.last_spawn = pg.time.get_ticks()
        self.paused = False

    def reset(self):
        self.__init__()