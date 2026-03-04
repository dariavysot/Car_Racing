import pygame as pg
from config import Settings as C
from core.game_object import GameObject

class PlayerCar(GameObject):
    def __init__(self, image):
        start_x = C.WIDTH // 2
        start_y = C.PLAYER_Y

        super().__init__(image, start_x, start_y)
        self.speed = C.PLAYER_LANE_SPEED

    def update(self, keys):
        if keys[pg.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pg.K_RIGHT]:
            self.rect.x += self.speed

        self.rect.x = max(0, min(self.rect.x, C.WIDTH - self.rect.width))

    def draw_with_light(self, screen, is_night):
        self.draw(screen)

        if not is_night:
            return

        light_height = 220
        top_width = int(self.rect.width * 0.6)
        bottom_width = int(self.rect.width * 1.6)

        light_surf = pg.Surface((bottom_width, light_height), pg.SRCALPHA)

        center_x = bottom_width // 2

        for y in range(light_height):
            progress = y / light_height

            current_width = top_width + (bottom_width - top_width) * progress

            alpha = int(90 * (1 - progress) ** 2)

            x1 = int(center_x - current_width / 2)
            x2 = int(center_x + current_width / 2)

            pg.draw.line(
                light_surf,
                (255, 255, 200, alpha),
                (x1, light_height - y),
                (x2, light_height - y)
            )

        screen.blit(
            light_surf,
            (self.rect.centerx - bottom_width // 2,
            self.rect.top - light_height + 5)
        )