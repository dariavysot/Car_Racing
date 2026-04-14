from unittest.mock import MagicMock, call, patch

import pygame as pg
import pytest

from config import Settings as C
from managers.sound_manager import SoundManager

pytestmark = [pytest.mark.component, pytest.mark.sound]


@pytest.fixture(autouse=True)
def mock_pygame_mixer():
    with patch("pygame.mixer.init") as mock_init, patch(
        "pygame.mixer.music.load"
    ) as mock_music_load, patch(
        "pygame.mixer.music.set_volume"
    ) as mock_music_set_vol, patch(
        "pygame.mixer.music.play"
    ) as mock_music_play, patch(
        "pygame.mixer.music.pause"
    ) as mock_music_pause, patch(
        "pygame.mixer.music.unpause"
    ) as mock_music_unpause, patch(
        "pygame.mixer.stop"
    ) as mock_mixer_stop, patch(
        "pygame.mixer.Sound"
    ) as mock_sound_class:

        mock_engine = MagicMock(name="MockEngineSound")
        mock_crash = MagicMock(name="MockCrashSound")
        mock_button = MagicMock(name="MockButtonSound")

        mock_sound_class.side_effect = [mock_engine, mock_crash, mock_button]

        mock_sound_play = MagicMock(name="mock_sound_play")
        mock_sound_play.return_value = MagicMock(spec=pg.mixer.Channel)

        mock_engine.play = mock_sound_play
        mock_crash.play = mock_sound_play
        mock_button.play = mock_sound_play

        yield {
            "init": mock_init,
            "music_load": mock_music_load,
            "music_set_vol": mock_music_set_vol,
            "music_play": mock_music_play,
            "music_pause": mock_music_pause,
            "music_unpause": mock_music_unpause,
            "mixer_stop": mock_mixer_stop,
            "sound_class": mock_sound_class,
            "sound_play": mock_sound_play,
            "engine": mock_engine,
            "crash": mock_crash,
            "button": mock_button,
        }


@pytest.fixture
def sound_manager(mock_pygame_mixer):
    sm = SoundManager()
    sm._mocks = mock_pygame_mixer
    sm._mock_engine = mock_pygame_mixer["engine"]
    sm._mock_crash = mock_pygame_mixer["crash"]
    sm._mock_button = mock_pygame_mixer["button"]
    return sm


@pytest.fixture
def mock_channel():
    return MagicMock(spec=pg.mixer.Channel)


@pytest.mark.init
def test_init_initializes_mixer_and_loads_assets(sound_manager, mock_pygame_mixer):
    mock_pygame_mixer["sound_class"].assert_has_calls(
        [
            call("assets/sounds/engine.wav"),
            call("assets/sounds/crash.wav"),
            call("assets/sounds/button.wav"),
        ],
        any_order=False,
    )

    mock_pygame_mixer["music_load"].assert_called_once_with(
        "assets/music/music0.ogg")
    mock_pygame_mixer["music_set_vol"].assert_called_once_with(0.5)

    assert sound_manager.engine_channel is None
    assert sound_manager.is_paused is False


def test_start_plays_music_and_engine_loop(sound_manager, mock_pygame_mixer):
    sound_manager.start()

    mock_pygame_mixer["music_play"].assert_called_once_with(-1)
    mock_pygame_mixer["sound_play"].assert_called_once_with(-1)

    assert sound_manager.engine_channel is not None


def test_reset_stops_all_and_restarts(sound_manager, mock_pygame_mixer):
    with patch.object(sound_manager, "start") as mock_start:
        sound_manager.reset()

        mock_pygame_mixer["mixer_stop"].assert_called_once()
        mock_start.assert_called_once()


@pytest.mark.update
@pytest.mark.parametrize(
    "speed, expected_volume",
    [
        (0, 0.0),
        (C.MAX_SPEED_RATING / 2, 0.5),
        (C.MAX_SPEED_RATING, 1.0),
        (C.MAX_SPEED_RATING * 1.5, 1.0),
        (-50, 0.0),
        (-0.1, 0.0),
    ],
    ids=["zero", "half", "max", "over", "negative", "tiny_negative"],
)
def test_update_engine_volume(sound_manager, mock_channel, speed, expected_volume):
    sound_manager.engine_channel = mock_channel

    sound_manager.update_engine(speed)

    mock_channel.set_volume.assert_called_once()
    actual_volume = mock_channel.set_volume.call_args[0][0]
    assert 0.0 <= actual_volume <= 1.0, f"Volume {actual_volume} out of [0,1] range"


@pytest.mark.update
def test_update_engine_no_channel(sound_manager):
    sound_manager.engine_channel = None
    sound_manager.update_engine(999)


def test_pause(sound_manager, mock_channel, mock_pygame_mixer):
    sound_manager.engine_channel = mock_channel
    sound_manager.pause()

    mock_pygame_mixer["music_pause"].assert_called_once()
    mock_channel.pause.assert_called_once()
    assert sound_manager.is_paused is True


def test_unpause(sound_manager, mock_channel, mock_pygame_mixer):
    sound_manager.engine_channel = mock_channel
    sound_manager.unpause()

    mock_pygame_mixer["music_unpause"].assert_called_once()
    mock_channel.unpause.assert_called_once()
    assert sound_manager.is_paused is False


def test_crash_plays_sound(sound_manager, mock_pygame_mixer):
    sound_manager.crash()
    mock_pygame_mixer["crash"].play.assert_called_once()


def test_click_plays_sound(sound_manager, mock_pygame_mixer):
    sound_manager.click()
    mock_pygame_mixer["button"].play.assert_called_once()


def test_pause_without_engine_channel(sound_manager, mock_pygame_mixer):
    sound_manager.engine_channel = None
    sound_manager.pause()
    mock_pygame_mixer["music_pause"].assert_called_once()
    assert sound_manager.is_paused is True


def test_unpause_without_engine_channel(sound_manager, mock_pygame_mixer):
    sound_manager.engine_channel = None
    sound_manager.unpause()
    mock_pygame_mixer["music_unpause"].assert_called_once()
    assert sound_manager.is_paused is False
