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
    
    def draw_with_light(self, screen, is_night):
        self.draw(screen)

        if not is_night:
            return

        # --- 1. DRAWING THE HEADLIGHTS  ---
        light_height = 220
        top_width = int(self.rect.width * 0.6)
        bottom_width = int(self.rect.width * 1.6)
        
        light_surf = pg.Surface((bottom_width, light_height), pg.SRCALPHA)
        center_x = bottom_width // 2

        main_color = (255, 255, 255)

        for y in range(light_height):
            progress = y / light_height
            alpha = int(120 * (1 - progress) ** 2)
            current_width = top_width + (bottom_width - top_width) * progress
            
            pg.draw.line(light_surf, (*main_color, alpha), 
                         (int(center_x - current_width/2), light_height - y), 
                         (int(center_x + current_width/2), light_height - y))

        if self.direction == "OPPOSITE":
            light_surf = pg.transform.flip(light_surf, False, True)
            screen.blit(light_surf, (self.rect.centerx - bottom_width // 2, self.rect.bottom - 5))
        else:
            screen.blit(light_surf, (self.rect.centerx - bottom_width // 2, self.rect.top - light_height + 5))

        # --- 2. DRAWING THE REAR RED LIGHTS ---
        back_y = self.rect.top + 3 if self.direction == "OPPOSITE" else self.rect.bottom - 3
        
        dot_radius = 2
        glow_radius = 5
        
        for offset in [-self.rect.width // 3.5, self.rect.width // 3.5]:
            pos = (self.rect.centerx + offset, back_y)

            pg.draw.circle(screen, (255, 100, 100), pos, dot_radius)

            glow_surf = pg.Surface((glow_radius * 2, glow_radius * 2), pg.SRCALPHA)
            pg.draw.circle(glow_surf, (200, 0, 0, 80), (glow_radius, glow_radius), glow_radius)

            screen.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius), special_flags=pg.BLEND_RGB_ADD)