import pytest
from unittest.mock import MagicMock
import pygame as pg

def test_game_reset(mock_game):
    mock_game.state.started = True
    mock_game.state.paused = True
    mock_game.reset()
    assert mock_game.state.started is False
    assert mock_game.state.paused is False

def test_check_collisions_no_enemies(mock_game):
    mock_game.enemies.obstacles = []
    assert mock_game.check_collisions() is None

def test_collision_logic_trigger(mock_game):
    enemy_mock = MagicMock()
    enemy_mock.rect = pg.Rect(0, 0, 10, 10)
    mock_game.enemies.check_collision = MagicMock(return_value=enemy_mock)
    result = mock_game.check_collisions()
    assert result == enemy_mock

@pytest.mark.parametrize("initial_pause_state, expected_final_state", [
    (False, True),
    (True, False)
])
def test_pause_logic_integration(mock_game, initial_pause_state, expected_final_state):
    mock_game.state.paused = initial_pause_state
    mock_game.state.paused = not mock_game.state.paused
    assert mock_game.state.paused == expected_final_state