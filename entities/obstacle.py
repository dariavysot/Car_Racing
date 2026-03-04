import pygame as pg
from core.game_object import GameObject
from config import Settings as C

class Obstacle(GameObject):
    def __init__(self, image, lane, y, speed):
        self.lane = lane
        self.speed = speed
        x = C.LANE_WIDTH * lane + C.LANE_WIDTH // 2
        super().__init__(image, x, y)

    def update(self, dt_sec):
        self.rect.y += self.speed * dt_sec

    def is_out(self):
        return self.rect.y >= C.HEIGHT + C.CAR_HEIGHT

    def collides(self, player_rect):
        return self.rect.colliderect(player_rect)
    
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

            # малюємо знизу вгору
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