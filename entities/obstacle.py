import pygame as pg
from config import Settings as C

class Obstacle:
    def __init__(self, image, lane, y, speed, obstacle_type="CAR"):
        self.image = image
        self.lane = lane
        self.speed = speed

        if obstacle_type == "TRACK":
            self.image = pg.transform.smoothscale(self.image, (C.CAR_WIDTH, C.TRACK_HEIGHT))
        else:
            self.image = pg.transform.smoothscale(self.image, (C.CAR_WIDTH, C.CAR_HEIGHT))

        x = C.LANE_WIDTH * lane + (C.LANE_WIDTH - C.CAR_WIDTH) // 2
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt_sec):
        self.rect.y += self.speed * dt_sec

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_out(self):
        return self.rect.y >= C.HEIGHT + C.CAR_HEIGHT

    def collides(self, player_rect):
        return self.rect.colliderect(player_rect)