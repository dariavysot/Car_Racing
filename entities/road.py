from config import Settings as C

class Road:
    def __init__(self, image):
        self.image = image
        self.y1 = 0
        self.y2 = -C.HEIGHT

    def update(self):
        self.y1 += C.ROAD_SCROLL
        self.y2 += C.ROAD_SCROLL

        if self.y1 >= C.HEIGHT:
            self.y1 = self.y2 - C.HEIGHT
        if self.y2 >= C.HEIGHT:
            self.y2 = self.y1 - C.HEIGHT

    def draw(self, screen):
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))