from unittest.mock import MagicMock, patch

import pygame as pg
import pytest

from logic import Game


@pytest.fixture
def mock_game():
    """Глобальна фікстура для ініціалізації гри в headless режимі."""
    fake_surface = pg.Surface((10, 10))

    # Створюємо Mock для зображень
    mock_surface_obj = MagicMock(spec=pg.Surface)
    mock_surface_obj.convert_alpha.return_value = fake_surface
    mock_surface_obj.get_rect.return_value = fake_surface.get_rect()

    # Мокаємо все залізо (відео, звук, файли)
    with patch("pygame.display.set_mode"), patch("pygame.display.set_caption"), patch(
        "pygame.display.set_icon"
    ), patch("pygame.image.load", return_value=mock_surface_obj), patch(
        "pygame.font.SysFont"
    ), patch(
        "pygame.transform.smoothscale", return_value=fake_surface
    ), patch(
        "os.path.exists", return_value=True
    ), patch(
        "pygame.mixer.init"
    ), patch(
        "pygame.mixer.stop"
    ), patch(
        "logic.SoundManager"
    ) as mock_sound_class:

        mock_sound_instance = mock_sound_class.return_value
        pg.font.init()

        game = Game()
        game.sounds = mock_sound_instance

        yield game
