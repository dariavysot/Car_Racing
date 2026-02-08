import random
from config import Settings as C

class ObstacleManager:
    def __init__(self, image):
        self.image = image
        self.enemies = []

        self.lane_xpos = [
            C.LANE_WIDTH * i + (C.LANE_WIDTH - C.CAR_WIDTH) // 2
            for i in range(C.LANES)
        ]

    def spawn(self):
        lanes = random.choices(self.lane_xpos, k=C.MAX_ENEMIES)
        for l in lanes:
            rect = self.image.get_rect(topleft=(l, -C.CAR_HEIGHT))
            self.enemies.append(rect)

    def update(self):
        for r in self.enemies:
            r.y += C.ENEMY_SPEED
        self.enemies = [r for r in self.enemies if r.y < C.HEIGHT + C.CAR_HEIGHT]

    def check_collision(self, player_rect):
        for r in self.enemies:
            if player_rect.colliderect(r):
                return r
        return None

    def draw(self, screen):
        for r in self.enemies:
            screen.blit(self.image, r)