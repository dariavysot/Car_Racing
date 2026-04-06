import pytest
import pygame as pg
from unittest.mock import MagicMock, patch
from gameplay.two_players import TwoPlayersGame


@pytest.mark.physics
class TestVersusGame:
    """Tests for the dual-player competitive mode and inter-player interactions."""

    @pytest.fixture
    def mock_versus_game(self):
        """Fixture providing a two-player game instance with mocked dependencies."""
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

    def test_versus_initialization(self, mock_versus_game):
        """Verification of independent control schemes for both players."""
        assert hasattr(mock_versus_game, 'player1')
        assert hasattr(mock_versus_game, 'player2')
        assert mock_versus_game.player1.left_key == pg.K_a
        assert mock_versus_game.player2.left_key == pg.K_LEFT

    def test_collision_between_players(self, mock_versus_game):
        """Detection of physical contact between player entities."""
        mock_versus_game.player1.rect = pg.Rect(100, 100, 40, 70)
        mock_versus_game.player2.rect = pg.Rect(100, 100, 40, 70)

        mock_versus_game.check_collisions()
        assert mock_versus_game.handle_result.called

    @pytest.mark.parametrize("p1_dir, p2_dir, expected_crash", [
        (1, 0, (True, False)),
        (0, -1, (False, True)),
        (0, 0, (True, True))
    ])
    def test_collision_result_scenarios(self, mock_versus_game, p1_dir, p2_dir, expected_crash):
        """Parameterized verification of winner/loser determination based on movement state."""
        mock_versus_game.player1.rect = pg.Rect(100, 100, 40, 70)
        mock_versus_game.player2.rect = pg.Rect(100, 100, 40, 70)

        mock_versus_game.player1.direction = p1_dir
        mock_versus_game.player2.direction = p2_dir

        mock_versus_game.check_collisions()
        mock_versus_game.handle_result.assert_called_with(*expected_crash)
