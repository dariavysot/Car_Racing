import pytest
import pygame as pg
from unittest.mock import MagicMock, patch
from config import Settings as C
from gameplay.two_players import TwoPlayersGame


@pytest.mark.unit
@pytest.mark.component
class TestVersusGame:
    """Comprehensive test suite for the TwoPlayersGame component."""

    @pytest.fixture
    def mock_versus_game(self):
        """Isolated fixture with mocked hardware and assets."""
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

    @pytest.mark.init
    def test_versus_initialization(self, mock_versus_game):
        """Check independent controls and starting positions."""
        assert hasattr(mock_versus_game, 'player1')
        assert hasattr(mock_versus_game, 'player2')

        assert mock_versus_game.player1.rect.centerx == C.WIDTH // 3
        assert mock_versus_game.player2.rect.centerx == C.WIDTH * 2 // 3

    @pytest.mark.unit
    @pytest.mark.component
    @pytest.mark.entities
    def test_get_player_rects(self, mock_versus_game):
        """Ensure get_player_rects returns a list
        containing both players' current rectangles."""
        rects = mock_versus_game.get_player_rects()
        assert rects == [mock_versus_game.player1.rect,
                         mock_versus_game.player2.rect]

    @pytest.mark.collision
    @pytest.mark.logic
    @pytest.mark.parametrize("p1_dir, p2_dir, expected", [
        (1, 0, (True, False)),
        (0, -1, (False, True)),
        (0, 0, (True, True))
    ])
    def test_player_vs_player_collision(
            self, mock_versus_game, p1_dir, p2_dir, expected):
        """Verify fault determination in player-to-player contact."""
        mock_versus_game.player1.rect = pg.Rect(100, 100, 40, 70)
        mock_versus_game.player2.rect = pg.Rect(100, 100, 40, 70)
        mock_versus_game.player1.direction = p1_dir
        mock_versus_game.player2.direction = p2_dir

        mock_versus_game.check_collisions()
        mock_versus_game.handle_result.assert_called_with(*expected)

    @pytest.mark.collision
    @pytest.mark.obstacles
    @pytest.mark.parametrize("crash1, crash2", [
        (True, False),
        (False, True),
        (True, True)
    ])
    def test_traffic_collision_logic(self, mock_versus_game, crash1, crash2):
        """Verify win/loss results when interacting with NPC traffic."""
        mock_versus_game.enemies.check_collision = MagicMock(
            side_effect=lambda rect: (
                crash1 if rect == mock_versus_game.player1.rect else crash2
            )
        )

        mock_versus_game.check_collisions()
        mock_versus_game.handle_result.assert_called_with(crash1, crash2)

    @pytest.mark.collision
    def test_no_collision(self, mock_versus_game):
        """Ensure no result is triggered when no collisions occur."""
        mock_versus_game.player1.rect = pg.Rect(0, 0, 40, 70)
        mock_versus_game.player2.rect = pg.Rect(200, 200, 40, 70)

        enemies = mock_versus_game.enemies
        enemies.check_collision = MagicMock(return_value=False)

        mock_versus_game.check_collisions()

        mock_versus_game.handle_result.assert_not_called()

    @pytest.mark.update
    def test_movement_boundaries(self, mock_versus_game):
        """Ensure players are clamped within the screen width."""
        mock_versus_game.player1.rect.x = -500
        mock_versus_game.player2.rect.x = C.WIDTH + 500

        mock_keys = MagicMock()
        mock_keys.__getitem__.return_value = False

        mock_versus_game.update_players(mock_keys, 0.1)

        assert mock_versus_game.player1.rect.x == 0
        assert mock_versus_game.player2.rect.x == C.WIDTH - \
               mock_versus_game.player2.rect.width

    @pytest.mark.draw
    def test_rendering_layer_calls(self, mock_versus_game):
        """Verify that all entities and lights trigger draw calls."""

        with patch.object(mock_versus_game.player1, 'draw') as p1_draw, \
                patch.object(mock_versus_game.player2, 'draw') as p2_draw:
            mock_versus_game.draw_players()
            assert p1_draw.called and p2_draw.called

            with (patch.object(mock_versus_game.player1, 'draw_only_light')
                  as l1,
                  patch.object(mock_versus_game.player2, 'draw_only_light')
                  as l2):
                mock_versus_game.draw_player_lights()
                assert l1.called and l2.called

    @pytest.mark.draw
    def test_show_game_over_renders(self, mock_versus_game):
        """Ensure show_game_over renders UI elements."""
        mock_versus_game.screen = MagicMock()
        mock_versus_game.font_big = MagicMock()
        mock_versus_game.font_small = MagicMock()

        fake_surface = pg.Surface((10, 10))
        mock_versus_game.font_big.render.return_value = fake_surface
        mock_versus_game.font_small.render.return_value = fake_surface

        with patch('pygame.display.flip') as flip:
            mock_versus_game.show_game_over("TEST")

            assert mock_versus_game.font_big.render.called
            assert mock_versus_game.font_small.render.called
            assert mock_versus_game.screen.blit.called
            flip.assert_called_once()

    @pytest.mark.reset
    def test_reset_functionality(self, mock_versus_game):
        """Check if reset properly restores player initial states."""
        with patch('managers.asset_manager.AssetManager.load_car',
                   return_value=pg.Surface((10, 10))):
            mock_versus_game.player1.rect.x = 500
            mock_versus_game.reset_players()
        assert mock_versus_game.player1.rect.centerx == C.WIDTH // 3

    @pytest.mark.logic
    @pytest.mark.parametrize("c1, c2, expected_text", [
        (True, True, "DRAW!"),
        (True, False, "PLAYER 2 WINS!"),
        (False, True, "PLAYER 1 WINS!")
    ])
    def test_handle_result_branches(
            self, mock_versus_game, c1, c2, expected_text):
        """Coverage for all win/loss/draw text scenarios."""
        from logic import Game

        with patch.object(Game, 'wait_for_restart') as restart, \
                patch.object(Game, 'reset') as reset, \
                patch.object(TwoPlayersGame, 'show_explosion') as explosion, \
                patch.object(TwoPlayersGame, 'show_game_over') as ui:
            TwoPlayersGame.handle_result(mock_versus_game, c1, c2)

            ui.assert_called_once_with(expected_text)
            explosion.assert_called_once_with(c1, c2)
            restart.assert_called_once()
            reset.assert_called_once()
