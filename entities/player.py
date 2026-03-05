import pygame as pg
from config import Settings as C
from core.game_object import GameObject

class PlayerCar(GameObject):
    def __init__(self, image, left_key=pg.K_LEFT, right_key=pg.K_RIGHT):
        start_x = C.WIDTH // 2
        start_y = C.PLAYER_Y

        super().__init__(image, start_x, start_y)
        self.speed = C.PLAYER_LANE_SPEED
        self.left_key = left_key
        self.right_key = right_key
        self.direction = 0

    def update(self, keys):
        self.direction = 0

        if keys[self.left_key]:
            self.rect.x -= self.speed
            self.direction = -1

        if keys[self.right_key]:
            self.rect.x += self.speed
            self.direction = 1

        self.rect.x = max(0, min(self.rect.x, C.WIDTH - self.rect.width))

    def draw(self, screen):
        super().draw(screen)

    def draw_only_light(self, screen, is_night):
        self.draw_lights(screen, is_night, direction="SAME")