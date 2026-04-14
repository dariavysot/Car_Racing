import sys
from unittest.mock import MagicMock, patch

import pytest

from game_config import GameConfig

pytestmark = [pytest.mark.arguments]


@pytest.fixture
def mock_settings():
    with patch("game_config.C") as mock_c:
        mock_c.NUM_PLAYERS = 1
        mock_c.PLAYER_COLOR = "red"
        mock_c.PLAYER1_COLOR = "blue"
        mock_c.PLAYER2_COLOR = "red"
        mock_c.PLAYERS_COLORS = ["red"]
        mock_c.update_players_colors = MagicMock()
        yield mock_c


@pytest.mark.unit
@pytest.mark.parametrize(
    "argv, expected",
    [
        # 1. Default (no arguments)
        (
            ["script.py"],
            {
                "car_color": None,
                "players": None,
                "car1_color": None,
                "car2_color": None,
            },
        ),
        # 2. One player + color
        (
            ["script.py", "--car-color", "yellow"],
            {
                "car_color": "yellow",
                "players": None,
                "car1_color": None,
                "car2_color": None,
            },
        ),
        # 3. Two players (without colors)
        (
            ["script.py", "--players", "2"],
            {"car_color": None, "players": 2,
                "car1_color": None, "car2_color": None},
        ),
        # 4. Two players + colors
        (
            [
                "script.py",
                "--players",
                "2",
                "--car1-color",
                "green",
                "--car2-color",
                "purple",
            ],
            {
                "car_color": None,
                "players": 2,
                "car1_color": "green",
                "car2_color": "purple",
            },
        ),
    ],
    ids=["default", "single_player_color",
         "two_players_default", "two_players_custom"],
)
def test_parse_valid_arguments(argv, expected):
    """parse() works correctly."""
    with patch.object(sys, "argv", argv):
        args = GameConfig.parse()

        assert args.car_color == expected["car_color"]
        assert args.players == expected["players"]
        assert args.car1_color == expected["car1_color"]
        assert args.car2_color == expected["car2_color"]


@pytest.mark.unit
def test_parse_mutually_exclusive_car_color_and_players():
    """--car-color & --players 2 are not used together."""
    with patch.object(
        sys, "argv", ["script.py", "--car-color", "red", "--players", "2"]
    ), pytest.raises(SystemExit):
        GameConfig.parse()


@pytest.mark.unit
@pytest.mark.parametrize(
    "argv",
    [
        ["script.py", "--car1-color", "blue"],
        ["script.py", "--car2-color", "yellow"],
        ["script.py", "--car1-color", "blue", "--car2-color", "red"],
    ],
    ids=["car1_only", "car2_only", "both_without_players"],
)
def test_parse_car_colors_require_players_2(argv):
    """--car1-color / --car2-color require --players 2, else parser.error()."""
    with patch.object(sys, "argv", argv), pytest.raises(SystemExit):
        GameConfig.parse()


@pytest.mark.unit
def test_parse_invalid_color():
    """If color is not valid then argparse should throw SystemExit."""
    with patch.object(
        sys, "argv", ["script.py", "--car-color", "black"]
    ), pytest.raises(SystemExit):
        GameConfig.parse()


@pytest.mark.component
def test_apply_single_player_default(mock_settings):
    """One player with color by default (red)."""
    args = MagicMock()
    args.players = None
    args.car_color = None
    args.car1_color = None
    args.car2_color = None

    GameConfig.apply(args)

    assert mock_settings.NUM_PLAYERS == 1
    assert mock_settings.PLAYER_COLOR == "red"
    mock_settings.update_players_colors.assert_called_once()


@pytest.mark.component
def test_apply_single_player_custom_color(mock_settings):
    """One player with specified color (orange)."""
    args = MagicMock()
    args.players = None
    args.car_color = "orange"
    args.car1_color = None
    args.car2_color = None

    GameConfig.apply(args)

    assert mock_settings.NUM_PLAYERS == 1
    assert mock_settings.PLAYER_COLOR == "orange"
    mock_settings.update_players_colors.assert_called_once()


@pytest.mark.component
def test_apply_two_players_default_colors(mock_settings):
    """Two players with colors by default (red + blue)."""
    args = MagicMock()
    args.players = 2
    args.car_color = None
    args.car1_color = None
    args.car2_color = None

    GameConfig.apply(args)

    assert mock_settings.NUM_PLAYERS == 2
    assert mock_settings.PLAYER1_COLOR == "blue"
    assert mock_settings.PLAYER2_COLOR == "red"
    mock_settings.update_players_colors.assert_called_once()


@pytest.mark.component
def test_apply_two_players_custom_colors(mock_settings):
    """Two players with specified colors (green + purple)."""
    args = MagicMock()
    args.players = 2
    args.car_color = None
    args.car1_color = "green"
    args.car2_color = "purple"

    GameConfig.apply(args)

    assert mock_settings.NUM_PLAYERS == 2
    assert mock_settings.PLAYER1_COLOR == "green"
    assert mock_settings.PLAYER2_COLOR == "purple"
    mock_settings.update_players_colors.assert_called_once()
