import pygame as pg
from core.game_object import GameObject
from config import Settings as C

class Obstacle(GameObject):
    def __init__(self, image, lane, y, speed, direction="SAME"):
        self.lane = lane
        self.speed = speed
        self.direction = direction
        x = C.LANE_WIDTH * lane + C.LANE_WIDTH // 2
        super().__init__(image, x, y)

    def update(self, dt_sec):
        self.rect.y += self.speed * dt_sec

    def is_out(self):
        return self.rect.y >= C.HEIGHT + C.CAR_HEIGHT

    def collides(self, player_rect):
        return self.rect.colliderect(player_rect)

    def draw(self, screen):
        """
        Render the obstacle's body.

        Parameters
        ----------
        screen : pg.Surface
            Target surface for rendering.
        """
        super().draw(screen)

    def draw_only_light(self, screen, is_night):
        """
        Render only the lighting effects for the obstacle.

        This is used in the multi-pass rendering pipeline after the 
        darkness overlay is applied.

        Parameters
        ----------
        screen : pg.Surface
            Target surface for rendering.
        is_night : bool
            Activation flag for night mode effects.
        """
        self.draw_lights(screen, is_night, self.direction)