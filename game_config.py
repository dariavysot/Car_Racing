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

        args = parser.parse_args()
        GameConfig.apply(args)

    @staticmethod
    def apply(args):
        # color
        if args.car_color == "red":
            C.PLAYER_COLOR = C.RED
        elif args.car_color == "blue":
            C.PLAYER_COLOR = C.BLUE
        elif args.car_color == "yellow":
            C.PLAYER_COLOR = C.YELLOW
        elif args.car_color == "purple":
            C.PLAYER_COLOR = C.PURPLE
        elif args.car_color == "green":
            C.PLAYER_COLOR = C.GREEN
        
