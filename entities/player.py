import pygame as pg
from config import Settings as C

class Player:
    def __init__(self, image, car_w):
        self.image = image
        self.rect = image.get_rect(midbottom=(C.WIDTH // 2, C.HEIGHT - 50))
        self.car_w = car_w

    def update(self, keys):
        if keys[pg.K_LEFT]:
            self.rect.x -= C.CAR_SPEED
        if keys[pg.K_RIGHT]:
            self.rect.x += C.CAR_SPEED

        self.rect.x = max(0, min(C.WIDTH - self.car_w, self.rect.x))

    def draw(self, screen):
        screen.blit(self.image, self.rect)