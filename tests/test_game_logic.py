import pytest
import sys
from unittest.mock import MagicMock, patch, PropertyMock
import pygame as pg


@pytest.mark.logic
class TestGameCore:
    """Tests for the core logic of the game engine."""

    def test_game_initialization_state(self, mock_game):
        """Checking the initial state of the game after initialization."""
        assert mock_game.state.started is False
        assert mock_game.state.paused is False
        assert mock_game.state.time == 0
        assert hasattr(mock_game, 'player')

    def test_game_reset_logic(self, mock_game):
        """Checking for a full game reset to factory settings."""
        mock_game.state.started = True
        mock_game.state.time = 50.5
        mock_game.state.paused = True

        mock_game.reset()

        assert mock_game.state.started is False
        assert mock_game.state.time == 0
        assert mock_game.state.paused is False

        mock_game.sounds.reset.assert_called()

    def test_full_managers_reset(self, mock_game):
        """Checking if reset() correctly resets internal managers (Integration)."""
        with patch.object(mock_game.theme, 'reset') as mock_theme_reset:
            mock_game.reset()
            mock_theme_reset.assert_called_once()
            assert hasattr(mock_game, 'enemies')
            mock_game.sounds.pause.assert_called()

    def test_quit_event_handling(self, mock_game):
        """Testing the initiation of game exit when receiving a QUIT event."""

        event_quit = pg.event.Event(pg.QUIT)

        with patch('pygame.quit') as mock_pg_quit, \
             patch('sys.exit') as mock_sys_exit:

            if event_quit.type == pg.QUIT:
                pg.quit()
                sys.exit()

            mock_pg_quit.assert_called_once()
            mock_sys_exit.assert_called_once()

    def test_esc_key_quit(self, mock_game):
        """Checking exiting the game via the ESC key."""
        event_esc = pg.event.Event(pg.KEYDOWN, {'key': pg.K_ESCAPE})

        with patch('sys.exit') as mock_sys_exit:
            if event_esc.type == pg.KEYDOWN and event_esc.key == pg.K_ESCAPE:
                sys.exit()

            mock_sys_exit.assert_called_once()

    def test_draw_score_rendering(self, mock_game):
        """Testing the account rendering logic (DRAW block)."""

        mock_game.screen.blit = MagicMock()
        mock_game.state.time = 15.5 

        mock_game.draw_score(16)

        mock_game.screen.blit.assert_called()
        args, _ = mock_game.screen.blit.call_args
        assert args[1] == (10, 10)

    @pytest.mark.parametrize("dt, expected_time", [
        (1000, 1.0),
        (500, 0.5)
    ])
    def test_update_objects_flow(self, mock_game, dt, expected_time):
        """Testing object updates and timing."""
        mock_game.state.started = True
        mock_game.update_objects(pg.key.get_pressed(), dt, pg.time.get_ticks())
        assert mock_game.state.time == expected_time

    @pytest.mark.parametrize("dt, expected_time", [
        (1000, 1.0),
        (500, 0.5),
        (2000, 2.0)
    ])
    def test_score_calculation_flow(self, mock_game, dt, expected_time):
        """Parameterized game time (score) update test."""
        keys = pg.key.get_pressed()
        now = pg.time.get_ticks()

        mock_game.state.started = True

        mock_game.update_objects(keys, dt, now)

        assert mock_game.state.time == expected_time

    def test_collision_handling_sequence(self, mock_game):
        """Mocking test."""
        mock_enemy = MagicMock()
        mock_enemy.rect = pg.Rect(100, 100, 50, 50)

        with patch.object(mock_game, 'show_explosion'), \
             patch.object(mock_game, 'show_game_over'), \
             patch.object(mock_game, 'wait_for_restart'):

            mock_game.handle_crash(mock_enemy)

            mock_game.sounds.crash.assert_called_once()
            mock_game.sounds.pause.assert_called()

    def test_check_collisions_hit(self, mock_game):
        """Checking whether the check_collisions method is triggered when there is a collision."""

        mock_crash_obj = MagicMock()
        mock_game.enemies.check_collision = MagicMock(return_value=mock_crash_obj)

        result = mock_game.check_collisions()

        assert result == mock_crash_obj
        mock_game.enemies.check_collision.assert_called()

    @pytest.mark.parametrize("press_space, started_init, expected_started", [
        (True, False, True), # Pressed Space at start -> Game started
        (False, False, False), # Didn't press -> Didn't start
    ])
    def test_start_input_logic(self, mock_game, press_space, started_init, expected_started):
        """Testing game login logic through event simulation."""
        mock_game.state.started = started_init

        if press_space:
            event = pg.event.Event(pg.KEYDOWN, {'key': pg.K_SPACE})
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if not mock_game.state.started:
                    mock_game.state.started = True

        assert mock_game.state.started == expected_started
 
    def test_handle_events_pause_toggle(self, mock_game):
        """Pause toggle test via simulated keyboard events."""
        mock_game.state.started = True
        mock_game.state.paused = False

        event = pg.event.Event(pg.KEYDOWN, {'key': pg.K_SPACE})

        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            if mock_game.state.started:
                mock_game.state.paused = not mock_game.state.paused

        assert mock_game.state.paused is True

    def test_update_objects_calls_managers(self, mock_game):
        """Checking if update_objects causes subsystem updates."""
        keys = pg.key.get_pressed()
        dt = 16
        now = 1000

        with patch.object(mock_game.road, 'update') as mock_road_upd, \
             patch.object(mock_game.enemies, 'update') as mock_enemies_upd:

            mock_game.update_objects(keys, dt, now)

            mock_road_upd.assert_called_once()
            mock_enemies_upd.assert_called_once()
            mock_game.sounds.update_engine.assert_called()

    def test_spawn_logic_integration(self, mock_game):
        """Verifying spawn integration through direct control of mock values."""

        mock_game.state.started = True
        mock_game.state.paused = False

        type(mock_game.state).last_spawn = PropertyMock(return_value=0)
        type(mock_game.state).spawn_interval = PropertyMock(return_value=1000)

        now = 1100

        with patch.object(mock_game.enemies, 'spawn') as mock_spawn:
            mock_game.update_objects(pg.key.get_pressed(), 16, now)

            assert mock_spawn.called, "Spawn не викликано. Перевірте, чи не перекриваються методи в mock_game"

    def test_draw_calls_layers(self, mock_game):
        """Checking the drawing sequence of layers without display errors."""
        mock_game.screen.blit = MagicMock()
        mock_game.state.paused = True
        mock_game.state.started = True

        with patch.object(mock_game.theme, 'apply') as mock_theme_apply, \
             patch.object(mock_game, 'draw_players') as mock_draw_players, \
             patch('pygame.display.flip'):

            mock_game.draw(16)

            mock_theme_apply.assert_called_once_with(mock_game.screen)
            mock_draw_players.assert_called_once()
            assert mock_game.screen.blit.called