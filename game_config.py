"""
Command-line configuration module.

This module provides the `GameConfig` class to parse terminal arguments 
and apply them to the global game settings, allowing customization of 
player colors and game modes.
"""

import argparse
from config import Settings as C

class GameConfig:
    """
    Utility class for handling game initialization parameters.

    Parses command-line interface (CLI) arguments and synchronizes them 
    with the `Settings` class before the game engine starts.
    """

    @staticmethod
    def parse():
        """
        Define and parse available command-line arguments.
        
        Ensures logical consistency:
        - --car-color and --players 2 are mutually exclusive.
        - --car1-color and --car2-color require --players 2.
        """
        parser = argparse.ArgumentParser(description="Car Racing Game")

        # Color choices shared across parameters
        color_choices = ["red", "blue", "yellow", "orange", "purple", "green"]

        group = parser.add_mutually_exclusive_group()

        group.add_argument(
            "--car-color",
            choices=color_choices,
            help="Player car color (single-player mode only)"
        )

        parser.add_argument(
            "--players",
            type=int,
            choices=[1,2],
            default=1,
            help="Set to 2 for competitive mode"
        )

        parser.add_argument(
            "--car1-color",
            choices=color_choices,
            help="First player car color (two-player mode)"
        )

        parser.add_argument(
            "--car2-color",
            choices=color_choices,
            help="Second player car color (two-player mode)"
        )

        args = parser.parse_args()

        if args.players != 2:
            if args.car1_color or args.car2_color:
                parser.error("--car1-color and --car2-color require --players 2")

        GameConfig.apply(args)

    @staticmethod
    def apply(args):
        """
        Map parsed arguments to the global Settings class.

        Parameters
        ----------
        args : argparse.Namespace
            Object containing the values from the command-line flags.
        """
        num_players = 2 if args.players == 2 else 1
        C.NUM_PLAYERS = num_players

        if num_players == 1:
            # Configuration for competitive two-player mode
            C.PLAYER_COLOR = args.car_color or "red"
        else:
            # Fallback to defaults if specific colors aren't provided
            C.PLAYER1_COLOR = args.car1_color or "blue"
            C.PLAYER2_COLOR = args.car2_color or "red"