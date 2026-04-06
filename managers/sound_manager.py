import pygame as pg
from config import Settings as C


class SoundManager:
    """
    Controller for game audio, including background music and sound effects.

    This class handles the initialization, playback, and volume modulation
    of music and sound channels using pygame's mixer.

    Attributes
    ----------
    engine : pg.mixer.Sound
        Looping sound effect for the car engine.
    crash_sound : pg.mixer.Sound
        Sound effect played upon collision.
    button : pg.mixer.Sound
        Sound effect for UI interactions.
    engine_channel : pg.mixer.Channel or None
        The specific audio channel assigned to the engine sound.
    is_paused : bool
        Current pause state of the audio system.
    """

    def __init__(self):
        pg.mixer.init()

        pg.mixer.music.load("assets/music/music0.ogg")
        pg.mixer.music.set_volume(0.5)

        self.engine = pg.mixer.Sound("assets/sounds/engine.wav")
        self.crash_sound = pg.mixer.Sound("assets/sounds/crash.wav")
        self.button = pg.mixer.Sound("assets/sounds/button.wav")

        self.engine_channel = None
        self.is_paused = False

    def start(self):
        """
        Start background music and engine sound loops.
        """
        pg.mixer.music.play(-1)
        self.engine_channel = self.engine.play(-1)

    def reset(self):
        """
        Stop all audio and restart the primary game sounds.
        """
        pg.mixer.stop()
        self.start()

    def update_engine(self, speed):
        """
        Adjust engine volume dynamically based on car speed.

        Parameters
        ----------
        speed : float
            Current speed of the game.
        """
        if self.engine_channel:
            volume = min(speed / C.MAX_SPEED_RATING, 1)
            self.engine_channel.set_volume(volume)

    def pause(self):
        """
        Halt all music and active sound channels.
        """
        pg.mixer.music.pause()
        if self.engine_channel:
            self.engine_channel.pause()
        self.is_paused = True

    def unpause(self):
        """
        Resume music and sound channels from their last state.
        """
        pg.mixer.music.unpause()
        if self.engine_channel:
            self.engine_channel.unpause()
        self.is_paused = False

    def crash(self):
        """
        Play the collision sound effect.
        """
        self.crash_sound.play()

    def click(self):
        """
        Play the UI button click sound effect.
        """
        self.button.play()
