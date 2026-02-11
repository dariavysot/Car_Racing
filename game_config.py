import argparse
from config import Settings as C

class GameConfig:
    @staticmethod
    def parse():
        parser = argparse.ArgumentParser(description="Car Racing Game")

        parser.add_argument(
            "--car-color",
            choices=["red", "blue", "yellow", "purple", "green"],
            default="red",
            help="Player car color"
        )

        parser.add_argument(
            "--players",
            type=int,
            choices=[1, 2],
            default=1,
            help="Number of players (1 or 2)"
        )

        args = parser.parse_args()
        GameConfig.apply(args)

    @staticmethod
    def apply(args):
        # color
        color_map = {
            "red": C.RED,
            "blue": C.BLUE,
            "yellow": C.YELLOW,
            "purple": C.PURPLE,
            "green": C.GREEN,
        }

        C.PLAYER_COLOR = color_map[args.car_color]

        # number of players
        C.NUM_PLAYERS = args.players           
        
