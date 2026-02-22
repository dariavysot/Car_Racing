from config import Settings as C

class Obstacle:
    def __init__(self, image, x, y, speed):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = min(speed, C.MAX_SPEED)

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_out(self):
        return self.rect.y >= C.HEIGHT + C.CAR_HEIGHT

    def collides(self, player_rect):
        return self.rect.colliderect(player_rect)