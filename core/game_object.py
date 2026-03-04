# GameObject is a base class for all drawable/movable entities
# PlayerCar and Obstacle should inherit from it

import pygame as pg

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
        light_height = 220
        top_width = int(self.rect.width * 0.6)
        bottom_width = int(self.rect.width * 1.6)

        light_surf = pg.Surface((bottom_width, light_height), pg.SRCALPHA)
        center_x = bottom_width // 2
        main_color = (255, 255, 200)

        for y in range(light_height):
            progress = y / light_height

            alpha = int(130 * (1 - progress) ** 1.5)
            current_width = top_width + (bottom_width - top_width) * progress

            pg.draw.line(
                light_surf, 
                (*main_color, alpha), 
                (int(center_x - current_width/2), light_height - y), 
                (int(center_x + current_width/2), light_height - y)
            )

        if direction == "OPPOSITE":
            flipped_light = pg.transform.flip(light_surf, False, True)
            screen.blit(flipped_light, (self.rect.centerx - bottom_width // 2, self.rect.bottom - 5))
        else:
            screen.blit(light_surf, (self.rect.centerx - bottom_width // 2, self.rect.top - light_height + 5))

        # --- 2. REAR RED LIGHTS ---
        # Позиція залежить від напрямку (протилежна переднім фарам)
        back_y = self.rect.top + 3 if direction == "OPPOSITE" else self.rect.bottom - 3
        
        dot_radius = 2
        glow_radius = 5
        
        for offset in [-self.rect.width // 3.5, self.rect.width // 3.5]:
            pos = (int(self.rect.centerx + offset), int(back_y))
            
            pg.draw.circle(screen, (255, 100, 100), pos, dot_radius)
            
            glow_surf = pg.Surface((glow_radius * 2, glow_radius * 2), pg.SRCALPHA)
            pg.draw.circle(glow_surf, (200, 0, 0, 30), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius), special_flags=pg.BLEND_RGB_ADD)
