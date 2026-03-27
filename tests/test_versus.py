import pytest
import pygame as pg
from unittest.mock import MagicMock, patch
from gameplay.two_players import TwoPlayersGame
from config import Settings as C


@pytest.fixture
def mock_versus_game():
    """Фікстура для створення екземпляра гри на двох із заглушками."""
    fake_surface = pg.Surface((10, 10))
    mock_surface_obj = MagicMock(spec=pg.Surface)
    mock_surface_obj.convert_alpha.return_value = fake_surface
    mock_surface_obj.get_rect.return_value = fake_surface.get_rect()

    with patch('pygame.display.set_mode'), \
            patch('pygame.image.load', return_value=mock_surface_obj), \
            patch('pygame.font.SysFont'), \
            patch('pygame.mixer.init'), \
            patch('logic.SoundManager'):
        pg.font.init()
        game = TwoPlayersGame()
        game.handle_result = MagicMock()
        return game


@pytest.mark.physics
def test_versus_initialization(mock_versus_game):
    """Перевірка, чи ініціалізовано саме двох гравців."""
    assert hasattr(mock_versus_game, 'player1')
    assert hasattr(mock_versus_game, 'player2')
    assert mock_versus_game.player1.left_key == pg.K_a
    assert mock_versus_game.player2.left_key == pg.K_LEFT

@pytest.mark.physics
def test_collision_between_players(mock_versus_game):
    """Тест зіткнення двох гравців один з одним."""
    mock_versus_game.player1.rect = pg.Rect(100, 100, 40, 70)
    mock_versus_game.player2.rect = pg.Rect(100, 100, 40, 70)

    mock_versus_game.check_collisions()

    assert mock_versus_game.handle_result.called


@pytest.mark.parametrize("p1_dir, p2_dir, expected_crash", [
    (1, 0, (True, False)),
    (0, -1, (False, True)),
    (0, 0, (True, True))
])
def test_handle_result_logic_all_cases(mock_versus_game, p1_dir, p2_dir, expected_crash):
    """Параметризований тест для всіх варіантів зіткнення гравців."""
    mock_versus_game.player1.rect = pg.Rect(100, 100, 40, 70)
    mock_versus_game.player2.rect = pg.Rect(100, 100, 40, 70)

    mock_versus_game.player1.direction = p1_dir
    mock_versus_game.player2.direction = p2_dir

    mock_versus_game.check_collisions()

    mock_versus_game.handle_result.assert_called_with(*expected_crash)