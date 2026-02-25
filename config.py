class Settings:
    WIDTH, HEIGHT = 480, 720
    FPS = 60

    LANES = 6
    LANE_WIDTH = WIDTH / LANES

    CAR_WIDTH = int(WIDTH / (LANES * 1.4))
    CAR_HEIGHT = int(CAR_WIDTH * 1.7)

    TRUCK_HEIGHT = int(CAR_WIDTH * 2.4)

    PLAYER_LANE_SPEED = int(1800 / LANES)
    PLAYER_Y = int(HEIGHT - CAR_HEIGHT / 2) - 15

    WHITE = (255, 255, 255)
    GRAY = (120, 120, 120)
    RED = (220, 50, 50)
    BLUE = (40, 160, 255)
    YELLOW = (255, 220, 40)
    PURPLE = (160, 60, 255)
    GREEN = (60, 200, 80)
    ORANGE = (255, 140, 0)

    PLAYER_COLOR = "red"
    NUM_PLAYERS = 1