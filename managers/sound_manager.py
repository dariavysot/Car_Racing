import pygame as pg
from config import Settings as C

class SoundManager:

    def __init__(self):
        pg.mixer.init()

        pg.mixer.music.load("assets/music/music.ogg")
        pg.mixer.music.set_volume(0.5)

        self.engine = pg.mixer.Sound("assets/sounds/engine.wav")
        self.crash_sound = pg.mixer.Sound("assets/sounds/crash.wav")
        self.button = pg.mixer.Sound("assets/sounds/button.wav")

        self.engine_channel = None
        self.is_paused = False

    def start(self):
        pg.mixer.music.play(-1)
        self.engine_channel = self.engine.play(-1)

    def reset(self):
        pg.mixer.stop()
        self.start()

    def update_engine(self, speed):
        if self.engine_channel:
            volume = min(speed / C.MAX_SPEED_RATING, 1)
            self.engine_channel.set_volume(volume)

    def pause(self):
        pg.mixer.music.pause()
        if self.engine_channel:
            self.engine_channel.pause()
        self.is_paused = True

    def unpause(self):
        pg.mixer.music.unpause()
        if self.engine_channel:
            self.engine_channel.unpause()
        self.is_paused = False

    def crash(self):
        self.crash_sound.play()

    def click(self):
        self.button.play()