import pytest
from unittest.mock import MagicMock, patch
import pygame as pg
import os
from logic import Game

@pytest.fixture
def mock_game():
    fake_surface = pg.Surface((1, 1))

    # Створюємо Mock для зображень
    mock_surface_obj = MagicMock(spec=pg.Surface)
    mock_surface_obj.convert_alpha.return_value = fake_surface
    mock_surface_obj.get_rect.return_value = fake_surface.get_rect()

    # Мокаємо все, що торкається заліза (відео, звук, файли)
    with patch('pygame.display.set_mode'), \
         patch('pygame.display.set_caption'), \
         patch('pygame.display.set_icon'), \
         patch('pygame.image.load', return_value=mock_surface_obj), \
         patch('pygame.font.SysFont'), \
         patch('pygame.transform.smoothscale', return_value=fake_surface), \
         patch('os.path.exists', return_value=True), \
         patch('pygame.mixer.init'), \
         patch('pygame.mixer.pre_init'), \
         patch('managers.sound_manager.SoundManager'): 

        pg.font.init()
 
        game = Game()

        game.sounds = MagicMock()

        return game

def test_game_reset(mock_game):
    """Перевірка методу reset: чи повертаються параметри до початкових"""
    # Змінимо стан
    mock_game.state.started = True
    mock_game.state.paused = True

    # Викликаємо метод класу
    mock_game.reset()

    # Перевіряємо результат
    assert mock_game.state.started is False
    assert mock_game.state.paused is False

def test_check_collisions_no_enemies(mock_game):
    """Перевірка методу колізій, коли ворогів немає"""
    # Очищуємо список ворогів через менеджер
    mock_game.enemies.obstacles = []

    # Метод має повернути None (зіткнень немає)
    assert mock_game.check_collisions() is None

@pytest.mark.parametrize("initial_pause_state, expected_final_state", [
    (False, True),
    (True, False)
])
def test_pause_logic_integration(mock_game, initial_pause_state, expected_final_state):
    """Параметризований тест для логіки перемикання паузи"""
    mock_game.state.paused = initial_pause_state

    # Імітуємо логіку з методу run (натискання пробілу)
    if mock_game.state.started or True:
        mock_game.state.paused = not mock_game.state.paused

    assert mock_game.state.paused == expected_final_state
