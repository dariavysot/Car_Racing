"""
Core game engine module.

This module orchestrates the entire application lifecycle, including
resource management, state transitions, and the primary execution loop.
"""

import sys
import pygame as pg
from storage.highscore import HighScore

from config import Settings as C
from state import GameState
from managers.asset_manager import AssetManager
from managers.obstacle_manager import ObstacleManager
from managers.theme_manager import ThemeManager
from managers.sound_manager import SoundManager
from entities.road import Road
from entities.player import PlayerCar


class Game:
    """
    The main Application class.

    This class defines the stable game skeleton. It manages the integration
    of various systems like rendering, physics, and state logic.

    Attributes
    ----------
    screen : pg.Surface
        The main display surface.
    clock : pg.time.Clock
        The timing controller for frame rate regulation.
    state : GameState
        Container for current session data (score, speed, flags).
    theme : ThemeManager
        Controller for environmental Day/Night cycles.
    sounds: SoundManager
        Controller for music and sound effects.
    """

    def __init__(self):
        self.init_pygame()
        self.init_screen()
        self.init_fonts()
        self.load_assets()
        self.init_managers()
        self.reset()
        self.highscore = HighScore()

    # ----------------------------
    # INIT BLOCK
    # ----------------------------
    def init_pygame(self):
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.init()
        self.clock = pg.time.Clock()

    def init_screen(self):
        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Car Racing")
        pg.display.set_icon(pg.image.load("assets/images/icon.png"))

    def init_fonts(self):
        self.font_big = pg.font.SysFont("arial", 40, bold=True)
        self.font_small = pg.font.SysFont("arial", 24, bold=True)

    def init_managers(self):
        self.theme = ThemeManager()
        self.sounds = SoundManager()

    # ----------------------------
    # ASSETS BLOCK
    # ----------------------------
    def load_assets(self):
        """
        Load, scale, and cache all graphical resources for the game.

        This method acts as the centralized resource loader. It utilizes the
        AssetManager to fetch images from disk and performs smoothscaling
        to ensure all sprites (cars, trucks, road) align with the resolution
        defined in the global settings.

        The method also filters car colors to prevent the player's car sprite
        from appearing as an NPC obstacle.

        Notes
        -----
        - Player car is scaled to (C.CAR_WIDTH, C.CAR_HEIGHT).
        - NPC car sprites are stored in `self.car_images`.
        - Trucks are stored in `self.truck_images`
        and scaled to `C.TRUCK_HEIGHT`.
        """
        am = AssetManager
        self.road_img = am.load_road()
        self.player_img = am.load_car(C.PLAYER_COLOR)
        self.explosion_img = am.load_explosion()
        self.player_img = pg.transform.smoothscale(
            self.player_img, (C.CAR_WIDTH, C.CAR_HEIGHT))

        self.car_images = []
        self.truck_images = []
        colors = ["red", "blue", "yellow", "orange", "purple", "green"]
        for color in colors:
            if color not in C.PLAYERS_COLORS:
                self.car_images.append(am.load_car(color))
        self.car_images.append(am.load_taxi())
        for num in range(2):
            self.truck_images.append(am.load_truck(num))

    # ----------------------------
    # RESET BLOCK
    # ----------------------------
    def reset(self):
        """
        Restore the game session to its initial state.

        Clears active obstacles, resets the theme timer, and re-initializes
        the player and game state flags.
        """
        self.state = GameState()
        self.state.started = False
        self.state.paused = False

        self.theme.reset()
        self.reset_players()
        self.reset_enemies()
        self.reset_road()
        self.reset_sounds()

    def reset_players(self):
        self.player = PlayerCar(self.player_img)

    def update_players(self, keys, dt_sec):
        self.player.update(keys, dt_sec)

    def draw_players(self):
        self.player.draw(self.screen)

    def draw_player_lights(self):
        self.player.draw_only_light(self.screen, self.theme.is_night)

    def get_player_rects(self):
        return [self.player.rect]

    def reset_enemies(self):
        """Clear and re-initialize the obstacle management system."""
        self.enemies = ObstacleManager(self.car_images, self.truck_images)

    def reset_road(self):
        """Re-initialize the scrolling road background."""
        self.road = Road(self.road_img)

    def reset_sounds(self):
        self.sounds.reset()
        self.sounds.pause()

    # ----------------------------
    # UPDATE BLOCK
    # ----------------------------
    def update_objects(self, keys, dt, now):
        """
        Update the physics, input, and game state logic for one frame.

        This method is responsible for the 'Think' part of the game loop. It
        processes player movement, scrolls the background, manages the enemy
        spawning timer, and updates environmental themes.

        Parameters
        ----------
        keys : pygame.key.ScancodeWrapper
            The current keyboard state used for player control.
        dt : int
            Delta time in milliseconds since the last update, used to
            calculate frame-rate independent movement.
        now : int
            Current simulation time in milliseconds (pg.time.get_ticks()).

        Returns
        -------
        None

        Notes
        -----
        The method converts `dt` to seconds (`dt_sec`) before applying it
        to object updates to maintain a consistent speed regardless of FPS.
        """
        dt_sec = dt / 1000
        self.update_players(keys, dt_sec)
        self.road.update(dt_sec, self.state.speed)
        self.state.update(dt_sec)
        self.sounds.update_engine(self.state.speed)

        if now - self.state.last_spawn >= self.state.spawn_interval:
            self.enemies.spawn(
                self.state.max_enemies,
                self.get_player_rects(),
                self.state.speed
            )
            self.state.last_spawn = now

        self.enemies.update(dt_sec)
        self.theme.update(dt)

    def check_collisions(self):
        """Perform collision detection between the player and traffic."""
        for rect in self.get_player_rects():
            crash = self.enemies.check_collision(rect)
            if crash:
                return crash

        return None

    # ----------------------------
    # DRAW BLOCK
    # ----------------------------
    def draw(self, dt):
        """
        Orchestrate the visual composition of the game frame.

        Implements a multi-pass rendering technique to handle layering:
        1. Opaque Layer: Road and physical vehicle bodies.
        2. Filter Layer: Global theme (darkness) overlay.
        3. Additive Layer: Emissive light sources (headlights) that pierce
           the darkness.
        4. UI Layer: Score, pause messages, and start prompts.

        Parameters
        ----------
        dt : int
            Passed to `draw_score` for UI-related timing.

        Notes
        -----
        `pg.display.flip()` is called at the very end to update the window
        with the newly rendered frame.
        """
        self.screen.fill(C.GRAY)
        self.road.draw(self.screen)

        self.theme.apply(self.screen)
        self.enemies.draw(self.screen, self.theme.is_night)
        self.draw_players()
        self.draw_player_lights()

        self.draw_score(dt)

        if self.state.paused:
            paused_text = self.font_big.render("PAUSED", True, C.WHITE)
            rect = paused_text.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2))
            self.screen.blit(paused_text, rect)

        if not self.state.started:
            start_text = self.font_big.render(
                "Press SPACE to start", True, C.WHITE)
            rect = start_text.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2))
            self.screen.blit(start_text, rect)

        pg.display.flip()

    def draw_score(self, dt):
        """
        Calculate and render the current score on the screen.

        The score is dynamically calculated based on the total elapsed game
        time. It is rendered using a small font and positioned in the
        top-left corner of the display.

        Parameters
        ----------
        dt : int
            Time passed since the last frame in milliseconds. This is used
            for frame-rate independent calculations if necessary.

        Returns
        -------
        None

        Notes
        -----
        The score formula is: floor(game_time_seconds * 10).
        The text is blitted at a fixed offset of (10, 10) pixels from the
        top-left corner of the screen.
        """
        score = self.font_small.render(
            f"Score: {int(self.state.time * 10)}", True, C.WHITE
        )

        self.screen.blit(score, (10, 10))

    # ----------------------------
    # CRASH BLOCK
    # ----------------------------
    def handle_crash(self, enemy_rect):
        """
        Coordinate the sequence of events triggered by a player collision.

        This method manages the transition from active gameplay
        to the post-game state. It executes the visual crash effect, finalizes
        the session score, persists high score data, and enters the game-over
        interface loop.

        Parameters
        ----------
        enemy_rect : pg.Rect
            The collision source used for explosion positioning.

        Returns
        -------
        None
        """
        self.sounds.crash()
        self.sounds.pause()
        self.show_explosion(enemy_rect)
        final_score = int(self.state.time * 10)
        self.is_new_record = self.highscore.save_if_better(final_score)
        self.show_game_over()
        self.wait_for_restart()

    def show_explosion(self, enemy):
        """
        Render a static frame of the collision with an explosion effect.

        Freezes the game logic and draws the impact point between the player
        and the obstacle. This provides visual feedback of the crash before
        transitioning to the Game Over screen.

        Parameters
        ----------
        enemy : Obstacle
            The obstacle object that the player collided with, used to
            calculate the midpoint for the explosion sprite.

        Returns
        -------
        None

        Notes
        -----
        This method uses `pg.time.delay(700)` to halt the entire thread,
        giving the player time to register the collision.
        """
        mid = (
            (self.player.rect.centerx + enemy.rect.centerx) // 2,
            (self.player.rect.centery + enemy.rect.centery) // 2
        )

        self.road.draw(self.screen)

        self.theme.apply(self.screen)
        self.enemies.draw(self.screen, self.theme.is_night)
        self.player.draw(self.screen)
        self.player.draw_only_light(self.screen, self.theme.is_night)

        expl = pg.transform.smoothscale(self.explosion_img, (120, 120))
        self.screen.blit(expl, expl.get_rect(center=mid))
        pg.display.flip()
        pg.time.delay(700)

    def show_game_over(self):
        """
        Render and display the final game-over screen.

        Displays the "GAME OVER" title, the current high score, and a prompt
        to restart. If a new high score was achieved during the session,
        a "NEW RECORD!" announcement is shown.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        - Uses `pg.display.flip()` to ensure the final frame is visible to
          the player.
        - Centering is calculated based on `config.Settings.WIDTH` and
          `config.Settings.HEIGHT`.
        - Checks for the 'is_new_record' attribute to toggle the gold-colored
          record announcement.
        """
        cx, cy = C.WIDTH // 2, C.HEIGHT // 2

        game_over = self.font_big.render("GAME OVER", True, C.WHITE)
        self.screen.blit(game_over, game_over.get_rect(center=(cx, cy - 100)))

        if getattr(self, 'is_new_record', False):
            record_text = self.font_big.render(
                "NEW RECORD!", True, (255, 215, 0))
            self.screen.blit(
                record_text,
                record_text.get_rect(
                    center=(
                        cx,
                        cy)))

        hs_text = self.font_small.render(
            f"High Score: {
                self.highscore.value}",
            True,
            C.YELLOW)
        self.screen.blit(hs_text, hs_text.get_rect(center=(cx, cy + 60)))

        press = self.font_small.render(
            "Press any key to restart", True, C.WHITE)
        self.screen.blit(press, press.get_rect(center=(cx, cy + 120)))

        pg.display.flip()

    def wait_for_restart(self):
        """
        Halt execution in a blocking loop until a restart signal is received.

        This method enters a dedicated event loop after a crash, capturing
        input for restarting the game or performing a clean exit.

        Notes
        -----
        - Any key (except ESC) triggers a restart.
        - ESC or window close event triggers `sys.exit()`.
        - Internal clock is capped at 30 FPS
        to reduce CPU overhead while waiting.
        """
        waiting = True
        while waiting:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE:
                        pg.quit()
                        sys.exit()
                    else:
                        waiting = False
            self.clock.tick(30)

    # ----------------------------
    # MAIN LOOP
    # ----------------------------
    def run(self):
        """
        Execute the primary game loop.

        This method synchronizes input, physics, and rendering. It handles
        the master clock, processes events (start/pause/quit), and
        orchestrates the update-draw cycle.

        Notes
        -----
        - The loop frequency is capped by `config.Settings.FPS`.
        - Input handling is split between event polling (for toggles)
          and scancode state (for continuous movement).
        - Logic updates are conditionally executed based on the
          'started' and 'paused' flags.
        """
        running = True
        while running:
            dt = self.clock.tick(C.FPS)
            now = pg.time.get_ticks()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    running = False

                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_SPACE:
                        self.sounds.click()
                        if not self.state.started:
                            self.state.started = True
                            self.sounds.unpause()
                        else:
                            if not self.state.paused:
                                self.state.paused = True
                                self.sounds.pause()
                            else:
                                self.state.paused = False
                                self.sounds.unpause()
                    elif e.key == pg.K_ESCAPE:
                        running = False

            keys = pg.key.get_pressed()

            if self.state.started and not self.state.paused:
                self.update_objects(keys, dt, now)

                crashed = self.check_collisions()
                if crashed:
                    self.handle_crash(crashed)
                    self.reset()

            self.draw(dt)

        pg.quit()
        sys.exit()
