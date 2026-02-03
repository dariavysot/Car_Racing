import random
from config import Settings as C

class ObstacleManager:
    def __init__(self, image, car_w, car_h):
        self.image = image
        self.car_h = car_h
        self.enemies = []

        lanes = 3
        lane_w = C.WIDTH // lanes
        self.lane_xpos = [
            lane_w * i + (lane_w - car_w) // 2
            for i in range(lanes)
        ]

    def spawn(self):
        lane = random.choice(self.lane_xpos)
        rect = self.image.get_rect(topleft=(lane, -self.car_h))
        self.enemies.append(rect)

    def update(self):
        for r in self.enemies:
            r.y += C.ENEMY_SPEED
        self.enemies = [r for r in self.enemies if r.y < C.HEIGHT + self.car_h]

    def check_collision(self, player_rect):
        for r in self.enemies:
            if player_rect.colliderect(r):
                return r
        return None

    def draw(self, screen):
        for r in self.enemies:
            screen.blit(self.image, r)