import pytest
from state import GameState

def test_game_state_initialization():
    """Тест: чи правильно ініціалізується стан гри"""
    state = GameState()
    assert state.started is False
    assert state.paused is False
    # Перевіримо, чи початкова швидкість відповідає налаштуванням
    assert state.speed > 0

def test_pause_toggle_logic():
    """Тест: чи коректно працює логіка паузи"""
    state = GameState()
    
    # Імітуємо натискання пробілу (код з твого Game.run)
    state.paused = not state.paused
    assert state.paused is True
    
    state.paused = not state.paused
    assert state.paused is False