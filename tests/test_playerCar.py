import pytest
import pygame as pg
from config import Settings as C
from unittest.mock import MagicMock, patch
from logic import Game

@pytest.fixture
def mock_game():
    fake_surface = pg.Surface((10, 10))

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
         patch('pygame.mixer.stop'), \
         patch('logic.SoundManager') as mock_sound_class:

        # Налаштовуємо мок екземпляра
        mock_sound_instance = mock_sound_class.return_value

        pg.font.init()

        game = Game()
        game.sounds = mock_sound_instance

        return game


@pytest.mark.physics
def test_player_move_left(mock_game):
    """Перевірка руху вліво через метод update"""
    player = mock_game.player
    initial_x = player.rect.x

    keys = {player.left_key: True, player.right_key: False}

    player.update(keys, 0.1)

    assert player.rect.x < initial_x
    assert player.direction == -1

@pytest.mark.physics
def test_player_move_right(mock_game):
    """Перевірка руху вправо через метод update"""
    player = mock_game.player
    initial_x = player.rect.x

    keys = {player.left_key: False, player.right_key: True}

    player.update(keys, 0.1)

    assert player.rect.x > initial_x
    assert player.direction == 1


@pytest.mark.physics
def test_player_left_boundary(mock_game):
    """Перевірка обмеження зліва: x не може бути менше 0"""
    player = mock_game.player
    player.rect.x = -10

    keys = {player.left_key: False, player.right_key: False}
    player.update(keys, 0.1)

    assert player.rect.x == 0
    assert player.direction == 0


@pytest.mark.physics
def test_player_right_boundary(mock_game):
    """Перевірка обмеження справа: x не може вийти за край екрана"""
    player = mock_game.player
    player.rect.x = C.WIDTH + 100

    keys = {player.left_key: False, player.right_key: False}
    player.update(keys, 0.1)

    expected_x = C.WIDTH - player.rect.width
    assert player.rect.x == expected_x
    assert player.direction == 0