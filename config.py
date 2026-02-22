class Settings:
    WIDTH, HEIGHT = 480, 720
    FPS = 60

    LANES = 5
    LANE_WIDTH = WIDTH / LANES
    CAR_WIDTH = int(WIDTH / (LANES * 1.3))
    CAR_HEIGHT = int(CAR_WIDTH * 1.4)

    CAR_SPEED = int(30 / LANES)
    ROAD_SCROLL = 10

    WHITE = (255, 255, 255)
    GRAY = (120, 120, 120)
    RED = (220, 50, 50)
    BLUE = (40, 160, 255)
    YELLOW = (255, 220, 40)