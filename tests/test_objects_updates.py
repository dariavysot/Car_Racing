import pytest
from unittest.mock import patch, MagicMock, call
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

from logic import Game
from state import GameState

pytestmark = [
    pytest.mark.component,
    pytest.mark.logic
]

@pytest.fixture
def game():
    with patch.multiple('pygame', key=None):
        game_obj = Game()

        game_obj.update_players = MagicMock()
        game_obj.road = MagicMock()
        game_obj.state = MagicMock()
        game_obj.sounds = MagicMock()
        game_obj.enemies = MagicMock()
        game_obj.theme = MagicMock()
        game_obj.get_player_rects = MagicMock(return_value=[MagicMock()])

        game_obj.state.last_spawn = 0
        game_obj.state.spawn_interval = 1800
        game_obj.state.speed = 240
        game_obj.state.max_enemies = 0.3
        game_obj.state.paused = False

        return game_obj


@pytest.mark.update
def test_update_objects_calls_all_components(game):
    keys = MagicMock()
    dt = 16
    now = 5000

    game.update_objects(keys, dt, now)

    game.update_players.assert_called_once_with(keys, dt / 1000)
    game.road.update.assert_called_once_with(dt / 1000, game.state.speed)
    game.state.update.assert_called_once_with(dt / 1000)
    game.sounds.update_engine.assert_called_once_with(game.state.speed)

    game.enemies.update.assert_called_once_with(dt / 1000)
    game.theme.update.assert_called_once_with(dt)


@pytest.mark.spawn
def test_update_objects_spawns_enemy_when_interval_passed(game):
    keys = MagicMock()
    dt = 16
    now = 5000

    game.state.last_spawn = 1000
    game.state.spawn_interval = 1800

    game.update_objects(keys, dt, now)

    game.enemies.spawn.assert_called_once_with(
        game.state.max_enemies,
        game.get_player_rects.return_value,
        game.state.speed
    )
    assert game.state.last_spawn == now


@pytest.mark.spawn
def test_update_objects_does_not_spawn_if_interval_not_passed(game):
    keys = MagicMock()
    dt = 16
    now = 2500

    game.state.last_spawn = 1000
    game.state.spawn_interval = 1800

    game.update_objects(keys, dt, now)

    game.enemies.spawn.assert_not_called()
    assert game.state.last_spawn == 1000


@pytest.mark.update
def test_update_objects_dt_conversion(game):
    keys = MagicMock()
    dt = 30
    now = 10000

    game.update_objects(keys, dt, now)

    game.update_players.assert_called_once_with(keys, 0.03)
    game.road.update.assert_called_once_with(0.03, game.state.speed)
    game.state.update.assert_called_once_with(0.03)
    game.enemies.update.assert_called_once_with(0.03)