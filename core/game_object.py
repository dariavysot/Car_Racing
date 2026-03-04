# GameObject is a base class for all drawable/movable entities
# PlayerCar and Obstacle should inherit from it

import pygame as pg
from config import Settings as C

class GameObject:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = image.get_rect(center=(x, y))

    def update(self, *args, **kwargs):
        """Overridden in subclasses"""
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def draw_lights(self, screen, is_night, direction="SAME"):
        if not is_night:
            return

        # --- 1. HEADLIGHTS (Cone of light) ---
        top_width = int(self.rect.width * C.LIGHT_TOP_WIDTH_FACTOR)
        bottom_width = int(self.rect.width * C.LIGHT_BOTTOM_WIDTH_FACTOR)

        light_surf = pg.Surface((bottom_width, C.LIGHT_HEIGHT), pg.SRCALPHA)
        center_x = bottom_width // 2

        for y in range(C.LIGHT_HEIGHT):
            progress = y / C.LIGHT_HEIGHT

            alpha = int(C.NIGHT_ALPHA * (1 - progress) ** 1.5)
            current_width = top_width + (bottom_width - top_width) * progress

            pg.draw.line(
                light_surf, 
                (*C.LIGHT_COLOR, alpha), 
                (int(center_x - current_width/2), C.LIGHT_HEIGHT - y), 
                (int(center_x + current_width/2), C.LIGHT_HEIGHT - y)
            )

        if direction == "OPPOSITE":
            flipped_light = pg.transform.flip(light_surf, False, True)
            screen.blit(flipped_light, (self.rect.centerx - bottom_width // 2, self.rect.bottom - 5))
        else:
            screen.blit(light_surf, (self.rect.centerx - bottom_width // 2, self.rect.top - C.LIGHT_HEIGHT + 5))

        # --- 2. REAR RED LIGHTS ---
        back_y = self.rect.top + 3 if direction == "OPPOSITE" else self.rect.bottom - 3
        
        dot_radius = C.TAIL_LIGHT_DOT_RADIUS
        glow_radius = C.TAIL_LIGHT_GLOW_RADIUS
        
        for offset in [-self.rect.width // 3.5, self.rect.width // 3.5]:
            pos = (int(self.rect.centerx + offset), int(back_y))
            
            pg.draw.circle(screen, C.TAIL_LIGHT_COLOR, pos, dot_radius)
            
            glow_surf = pg.Surface((glow_radius * 2, glow_radius * 2), pg.SRCALPHA)
            pg.draw.circle(glow_surf, (200, 0, 0, 30), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius), special_flags=pg.BLEND_RGB_ADD)
