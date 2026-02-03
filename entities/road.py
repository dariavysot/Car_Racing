from config import Settings as C

class Road:
    def __init__(self, image):
        self.image = image
        self.y1 = 0
        self.y2 = -image.get_height()

    def update(self):
        self.y1 += C.ROAD_SCROLL
        self.y2 += C.ROAD_SCROLL

        if self.y1 >= C.HEIGHT:
            self.y1 = self.y2 - self.image.get_height()
        if self.y2 >= C.HEIGHT:
            self.y2 = self.y1 - self.image.get_height()

    def draw(self, screen):
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))