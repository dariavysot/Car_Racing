"""
Global game configuration and constants.

This module contains the `Settings` class which stores all hardcoded values,
dimensions, colors, and lighting parameters used across the application.
"""

from state import calculate_speed


class Settings:
    """
    Static container for game-wide constants.

    Organizes parameters into logical groups: display, gameplay physics,
    lighting effects, and color palettes.
    """
    # --- Display & Engine ---
    WIDTH, HEIGHT = 480, 720
    FPS = 60

    # --- Road & Lane Geometry ---
    LANES = 6
    LANE_WIDTH = WIDTH // LANES
    LANE_OFFSET = LANE_WIDTH // 2

    # --- Vehicle Dimensions ---
    CAR_WIDTH = int(WIDTH / (LANES * 1.6))
    CAR_HEIGHT = int(CAR_WIDTH * 2)
    TRUCK_HEIGHT = int(CAR_WIDTH * 2.4)

    # --- Gameplay Physics ---
    PLAYER_LANE_SPEED = int(1800 / LANES)
    PLAYER_Y = int(HEIGHT - CAR_HEIGHT / 2) - 15
    MAX_SPEED_RATING = calculate_speed(120)

    # --- Environment & Theme ---
    THEME_INTERVAL = 15000  # Time in ms between Day/Night cycles
    NIGHT_ALPHA = 130       # Global darkness overlay transparency (0-255)

    # --- Lighting FX (Headlights) ---
    LIGHT_HEIGHT = 220
    LIGHT_COLOR = (255, 255, 200)
    LIGHT_TOP_WIDTH_FACTOR = 0.6
    LIGHT_BOTTOM_WIDTH_FACTOR = 1.6

    # --- Lighting FX (Taillights) ---
    TAIL_LIGHT_DOT_RADIUS = 2
    TAIL_LIGHT_GLOW_RADIUS = 5
    TAIL_LIGHT_COLOR = (255, 100, 100)

    # --- Color Palette (RGB) ---
    WHITE = (255, 255, 255)
    GRAY = (120, 120, 120)
    RED = (220, 50, 50)
    BLUE = (40, 160, 255)
    YELLOW = (255, 220, 40)
    PURPLE = (160, 60, 255)
    GREEN = (60, 200, 80)
    ORANGE = (255, 140, 0)

    # --- Session State ---
    PLAYER_COLOR = "red"
    NUM_PLAYERS = 1
    PLAYER1_COLOR = "blue"
    PLAYER2_COLOR = "red"

    PLAYERS_COLORS = ["red"]

    @classmethod
    def update_players_colors(cls):
        if cls.NUM_PLAYERS == 1:
            cls.PLAYERS_COLORS = [cls.PLAYER_COLOR]
        else:
            cls.PLAYERS_COLORS = [cls.PLAYER1_COLOR, cls.PLAYER2_COLOR]
