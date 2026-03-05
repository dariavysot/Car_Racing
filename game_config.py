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

        Supported arguments:
        - --car-color: Color for single-player mode.
        - --car1-color: Color for Player 1 in competitive mode.
        - --car2-color: Color for Player 2 in competitive mode.
        - --players: Mode selector (1 for solo, 2 for versus).

        Returns
        -------
        None
            The method calls `apply()` internally to update global state.
        """
        parser = argparse.ArgumentParser(description="Car Racing Game")

        # Color choices shared across parameters
        color_choices = ["red", "blue", "yellow", "orange", "purple", "green"]

        parser.add_argument(
            "--car-color",
            choices=color_choices,
            default="red",
            help="Player car color (single-player mode)"
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
        """
        Map parsed arguments to the global Settings class.

        Parameters
        ----------
        args : argparse.Namespace
            Object containing the values from the command-line flags.
        """
        # Configuration for single-player mode
        if args.players == 1:
            C.PLAYER_COLOR = args.car_color

        # Configuration for competitive two-player mode
        else:
            # Fallback to defaults if specific colors aren't provided
            C.PLAYER1_COLOR = args.car1_color or "blue"
            C.PLAYER2_COLOR = args.car2_color or "red"

        # Update global player count setting
        C.NUM_PLAYERS = args.players
