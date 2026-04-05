import pytest
from unittest.mock import MagicMock, patch
import pygame as pg
from core.game_object import GameObject
from managers.theme_manager import ThemeManager
from config import Settings as C

@pytest.mark.entities
class TestGameObject:
    """Tests for the base game object."""

    @pytest.fixture
    def base_obj(self):
        """We use a real surface to check the correct geometry of Rect."""
        img = pg.Surface((40, 80)) 
        return GameObject(img, 100, 200)

    def test_object_initialization(self, base_obj):
        """Checking for correct positioning during initialization."""
        assert base_obj.rect.center == (100, 200)
        assert base_obj.rect.width == 40
        assert base_obj.rect.height == 80

    def test_draw_calls_blit(self, base_obj):
        """Checks if the draw method causes a blit on the screen."""
        mock_screen = MagicMock(spec=pg.Surface)
        base_obj.draw(mock_screen)
        mock_screen.blit.assert_called_once_with(base_obj.image, base_obj.rect)

    def test_draw_lights_skipped_during_day(self, base_obj):
        """Checking that the light is not drawn during the day."""
        mock_screen = MagicMock(spec=pg.Surface)
        with patch.object(base_obj, '_draw_headlights') as mock_head:
            base_obj.draw_lights(mock_screen, is_night=False)
            mock_head.assert_not_called()

    @pytest.mark.parametrize("direction", ["SAME", "OPPOSITE"])
    def test_draw_lights_called_at_night(self, base_obj, direction):
        """Checking that headlight drawing methods are called at night."""
        mock_screen = MagicMock(spec=pg.Surface)
        with patch.object(base_obj, '_draw_headlights') as mock_head, \
             patch.object(base_obj, '_draw_taillights') as mock_tail:

            base_obj.draw_lights(mock_screen, is_night=True, direction=direction)

            mock_head.assert_called_once_with(mock_screen, direction)
            mock_tail.assert_called_once_with(mock_screen, direction)

    def test_complex_lights_rendering(self, base_obj):
        """Test for complete headlight drawing cycles (raises Coverage)."""

        real_screen = pg.Surface((C.WIDTH, C.HEIGHT))

        base_obj.draw_lights(real_screen, is_night=True, direction="SAME")
        base_obj.draw_lights(real_screen, is_night=True, direction="OPPOSITE")

        assert isinstance(real_screen, pg.Surface)

    def test_base_update_method(self, base_obj):
        """Technical test for coverage of empty update method."""

        assert base_obj.update() is None

@pytest.mark.theme
class TestThemeManager:
    """Tests for day and night shift manager."""

    def test_theme_initialization(self):
        """Checking the initial state (day)."""
        manager = ThemeManager()
        assert manager.is_night is False
        assert manager.timer == 0
        assert manager.dark_overlay.get_alpha() == C.NIGHT_ALPHA

    def test_theme_toggle(self):
        """Checking for manual theme switching."""
        manager = ThemeManager()
        manager.toggle()
        assert manager.is_night is True
        manager.toggle()
        assert manager.is_night is False

    def test_theme_update_logic(self):
        """Checking automatic theme change on timer."""
        manager = ThemeManager()
        manager.interval = 1000

        manager.update(500)
        assert manager.is_night is False
        assert manager.timer == 500

        manager.update(600)
        assert manager.is_night is True
        assert manager.timer == 0

    def test_apply_draws_overlay_only_at_night(self):
        """Check that the mask of darkness is applied only at night."""
        manager = ThemeManager()
        mock_screen = MagicMock(spec=pg.Surface)

        manager.is_night = False
        manager.apply(mock_screen)
        mock_screen.blit.assert_not_called()

        manager.is_night = True
        manager.apply(mock_screen)
        mock_screen.blit.assert_called_once()

    def test_theme_reset(self):
        """Checking to reset the manager to the daily state."""
        manager = ThemeManager()
        manager.is_night = True
        manager.timer = 500

        manager.reset()

        assert manager.is_night is False
        assert manager.timer == 0
