from config import Settings as C

class Obstacle:
    def __init__(self, image, lane, y, speed):
        self.image = image
        self.lane = lane
        self.speed = speed

        x = C.LANE_WIDTH * lane + (C.LANE_WIDTH - C.CAR_WIDTH) // 2
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt_sec):
        px_per_sec = self.speed * C.FPS
        self.rect.y += px_per_sec * dt_sec

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_out(self):
        return self.rect.y >= C.HEIGHT + C.CAR_HEIGHT

    def collides(self, player_rect):
        return self.rect.colliderect(player_rect)