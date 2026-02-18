class Settings:
    WIDTH, HEIGHT = 480, 720
    FPS = 60

    CAR_SPEED = 10
    ROAD_SCROLL = 6
    ENEMY_SPEED = 4
    SPAWN_INTERVAL = 1400

    WHITE = (255, 255, 255)
    GRAY = (120, 120, 120)
    RED = (220, 50, 50)
    BLUE = (40, 160, 255)
    YELLOW = (255, 220, 40)
    PURPLE = (160, 60, 255)
    GREEN = (60, 200, 80)

    LANES = 3
    LANE_WIDTH = WIDTH // LANES

    CAR_WIDTH = int(LANE_WIDTH * 0.3)
    CAR_HEIGHT = int(CAR_WIDTH * 1.8)

    PLAYER_COLOR = RED
    NUM_PLAYERS = 1