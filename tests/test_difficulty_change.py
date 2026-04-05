import pytest
from unittest.mock import patch, MagicMock
import pygame as pg
import math

from state import GameState, calculate_speed

pytestmark = [
    pytest.mark.state
]

@pytest.fixture
def game_state():
    pg.init()
    state = GameState(base=240)
    yield state
    pg.quit()


@pytest.mark.unit
def test_calculate_speed_basic():
    assert calculate_speed(0) == 240
    assert calculate_speed(3) == pytest.approx(240 + math.log(4, 4) * 60, rel=1e-6)
    assert calculate_speed(15) == pytest.approx(240 + math.log(16, 4) * 60, rel=1e-6)


@pytest.mark.unit
def test_calculate_speed_with_custom_base():
    assert calculate_speed(0, base=300) == 300
    assert calculate_speed(3, base=180) == pytest.approx(180 + math.log(4, 4) * 60)


@pytest.mark.component
@pytest.mark.init
def test_game_state_initial_values(game_state):
    assert game_state.time == 0
    assert game_state.speed == 240
    assert game_state.max_enemies == 0.2
    assert game_state.spawn_interval == 1800
    assert game_state.paused is False
    assert game_state.started is False
    assert isinstance(game_state.last_spawn, int)


@pytest.mark.component
@pytest.mark.reset
def test_game_state_reset(game_state):
    game_state.time = 100
    game_state.speed = 500
    game_state.max_enemies = 0.5
    game_state.spawn_interval = 500

    game_state.reset()

    assert game_state.time == 0
    assert game_state.speed == 240
    assert game_state.max_enemies == 0.2
    assert game_state.spawn_interval == 1800


@pytest.mark.unit
@pytest.mark.update
def test_game_state_update_increases_time(game_state):
    dt = 0.16
    game_state.update(dt)
    assert game_state.time == pytest.approx(dt, rel=1e-9)


@pytest.mark.unit
@pytest.mark.update
def test_game_state_speed_increases_over_time(game_state):
    initial_speed = game_state.speed

    game_state.update(10.0)
    assert game_state.speed > initial_speed

    game_state.update(30.0)
    assert game_state.speed > initial_speed + 100


@pytest.mark.unit
@pytest.mark.update
def test_game_state_max_enemies_clamping(game_state):
    assert game_state.max_enemies == 0.2

    game_state.update(20)
    assert game_state.max_enemies >= 0.34

    game_state.update(100)
    assert game_state.max_enemies <= 0.67
    assert game_state.max_enemies >= 0.34


@pytest.mark.unit
@pytest.mark.update
@pytest.mark.spawn
def test_game_state_spawn_interval_decreases(game_state):
    initial_interval = game_state.spawn_interval

    game_state.update(10)
    assert game_state.spawn_interval < initial_interval

    game_state.time = 100
    game_state.update(0)
    assert game_state.spawn_interval == 1400


@pytest.mark.unit
@pytest.mark.spawn
@patch('pygame.time.get_ticks')
def test_game_state_last_spawn_is_set_on_init(mock_ticks):
    mock_ticks.return_value = 123456
    state = GameState()
    assert state.last_spawn == 123456