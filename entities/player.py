import pygame as pg
from config import Settings as C
from core.game_object import GameObject

class PlayerCar(GameObject):
    def __init__(self, image):
        start_x = C.WIDTH // 2
        start_y = C.PLAYER_Y

        super().__init__(image, start_x, start_y)
        self.speed = C.PLAYER_LANE_SPEED

    def update(self, keys, dt_sec):
        if keys[pg.K_LEFT]:
            self.rect.x -= self.speed * dt_sec
        if keys[pg.K_RIGHT]:
            self.rect.x += self.speed * dt_sec

        self.rect.x = max(0, min(self.rect.x, C.WIDTH - self.rect.width))