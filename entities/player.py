import pygame as pg
from config import Settings as C
from core.game_object import GameObject

class PlayerCar(GameObject):
    def __init__(self, image, car_w):
        start_x = C.WIDTH // 2
        start_y = C.HEIGHT - 50

        super().__init__(image, start_x, start_y)

        self.car_w = car_w
        self.speed = C.CAR_SPEED

    def update(self, keys):
        if keys[pg.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pg.K_RIGHT]:
            self.rect.x += self.speed

        self.rect.x = max(0, min(self.rect.x, C.WIDTH - self.car_w))