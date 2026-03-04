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

    def draw(self, screen):
        super().draw(screen)

    def draw_only_light(self, screen, is_night):

        if not is_night:
            return

        # --- 1. DRAWING THE HEADLIGHTS  ---
        light_height = 220
        top_width = int(self.rect.width * 0.6)
        bottom_width = int(self.rect.width * 1.6)

        light_surf = pg.Surface((bottom_width, light_height), pg.SRCALPHA)
        center_x = bottom_width // 2

        for y in range(light_height):
            progress = y / light_height

            alpha = int(130 * (1 - progress) ** 1)
            current_width = top_width + (bottom_width - top_width) * progress

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

        # --- 2. DRAWING THE REAR RED LIGHTS ---
        back_y = self.rect.bottom - 3
        dot_radius = 2
        glow_radius = 5
        
        for offset in [-self.rect.width // 3.5, self.rect.width // 3.5]:
            pos = (int(self.rect.centerx + offset), back_y)
            
            pg.draw.circle(screen, (255, 100, 100), pos, dot_radius)
            
            glow_surf = pg.Surface((glow_radius * 2, glow_radius * 2), pg.SRCALPHA)
            pg.draw.circle(glow_surf, (200, 0, 0, 40), (glow_radius, glow_radius), glow_radius)
            
            screen.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius), special_flags=pg.BLEND_RGB_ADD)