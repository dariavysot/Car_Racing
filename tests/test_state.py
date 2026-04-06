import pytest
from state import GameState


@pytest.mark.state
class TestGameState:
    def test_game_state_initialization(self):
        """Checking for clean initial values."""
        state = GameState()
        assert state.started is False
        assert state.paused is False
        assert state.time == 0

    def test_pause_toggle_logic(self):
        """Checking the pause switching logic."""
        state = GameState()
        state.paused = True
        assert state.paused is True
        state.paused = False
        assert state.paused is False

    def test_update_logic(self):
        """Checking update time and speed."""
        state = GameState(base=240)
        state.update(1.0)  # 1 second has passed
        assert state.time == 1.0
        assert state.speed > 240
