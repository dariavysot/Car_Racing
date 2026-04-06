import pytest
import pygame as pg
from config import Settings as C
from unittest.mock import MagicMock, patch
from logic import Game


@pytest.mark.physics
class TestSinglePlayerGame:
    """Tests for the single-player game mode and core player mechanics."""

    @pytest.fixture
    def mock_game(self):
        """Isolated game instance with mocked hardware components
        (video, audio, assets)."""
        fake_surface = pg.Surface((10, 10))
        mock_surface_obj = MagicMock(spec=pg.Surface)
        mock_surface_obj.convert_alpha.return_value = fake_surface
        mock_surface_obj.get_rect.return_value = fake_surface.get_rect()

        with patch('pygame.display.set_mode'), \
                patch('pygame.display.set_caption'), \
                patch('pygame.display.set_icon'), \
                patch('pygame.image.load', return_value=mock_surface_obj), \
                patch('pygame.font.SysFont'), \
                patch('pygame.transform.smoothscale',
                      return_value=fake_surface), \
                patch('os.path.exists', return_value=True), \
                patch('pygame.mixer.init'), \
                patch('pygame.mixer.stop'), \
                patch('logic.SoundManager') as mock_sound_class:
            mock_sound_instance = mock_sound_class.return_value
            pg.font.init()

            game = Game()
            game.sounds = mock_sound_instance
            return game

    def test_player_movement_logic(self, mock_game):
        """Verification of player positioning
        and direction during left/right movement."""
        player = mock_game.player

        # Test Move Left
        initial_x = player.rect.x
        player.update(
            {player.left_key: True, player.right_key: False}, 0.1)
        assert player.rect.x < initial_x
        assert player.direction == -1

        # Test Move Right
        player.update(
            {player.left_key: False, player.right_key: True}, 0.1)
        assert player.direction == 1

    def test_player_boundary_constraints(self, mock_game):
        """Ensures the player car remains
        within the horizontal window limits."""
        player = mock_game.player

        # Left boundary check
        player.rect.x = -10
        player.update({player.left_key: False, player.right_key: False}, 0.1)
        assert player.rect.x == 0

        # Right boundary check
        player.rect.x = C.WIDTH + 100
        player.update({player.left_key: False, player.right_key: False}, 0.1)

        expected_x = C.WIDTH - player.rect.width
        assert player.rect.x == expected_x
