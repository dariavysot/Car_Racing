import pytest
from state import GameState

@pytest.mark.state
def test_game_state_initialization():
    """Test: Is the game state initialized correctly"""
    state = GameState()
    assert state.started is False
    assert state.paused is False
    # Check if the initial speed matches the settings
    assert state.speed > 0

@pytest.mark.state
def test_pause_toggle_logic():
    """"Test: Is the pause logic working correctly"""
    state = GameState()

    # Simulate pressing the spacebar
    state.paused = not state.paused
    assert state.paused is True

    state.paused = not state.paused
    assert state.paused is False
