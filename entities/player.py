import pygame as pg
from config import Settings as C

class Player:
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect(midbottom=(C.WIDTH // 2, C.HEIGHT - 50))

    def update(self, keys):
        if keys[pg.K_LEFT]:
            self.rect.x -= C.CAR_SPEED
        if keys[pg.K_RIGHT]:
            self.rect.x += C.CAR_SPEED

        self.rect.x = max(0, min(C.WIDTH - C.CAR_WIDTH, self.rect.x))

    def draw(self, screen):
        screen.blit(self.image, self.rect)