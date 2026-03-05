"""
Two-player competitive mode for the Car Racing game.

This module provides the `TwoPlayersGame` class, which manages a separate
game loop where two players can race simultaneously on the same screen,
avoiding obstacles and competing for survival.
"""

import pygame as pg
import sys

from config import Settings as C
from state import GameState
from managers.obstacle_manager import ObstacleManager
from entities.road import Road
from entities.player import PlayerCar
from managers.asset_manager import AssetManager


class TwoPlayersGame:
    """
    Manager for the two-player competitive racing mode.

    This class coordinates the game loop, player movements, obstacle
    generation, and collision resolution for a split-lane racing
    environment.

    Parameters
    ----------
    assets : dict
        A dictionary containing shared game resources. Expected keys:
        - 'screen': pg.Surface, the main display surface.
        - 'clock': pg.time.Clock, game timing controller.
        - 'font_big', 'font_small': pg.font.Font, text rendering assets.
        - 'road', 'cars', 'trucks', 'explosion': pg.Surface or list,
          graphical assets loaded via AssetManager.

    Attributes
    ----------
    player1, player2 : PlayerCar
        The two competing player instances with distinct controls.
    enemies : ObstacleManager
        The system responsible for spawning and updating traffic.
    state : GameState
        Tracks session data like speed, difficulty, and pause status.
    """
    def __init__(self, assets):
        """
        Initialize the TwoPlayersGame instance.

        Sets up the display surface, timing controls, and loads all necessary
        graphical and text assets from the provided shared resource dictionary.

        Parameters
        ----------
        assets : dict
            A dictionary containing shared game resources. Expected keys:

            - 'screen' : pygame.Surface
                The main window surface for rendering.
            - 'clock' : pygame.time.Clock
                The clock object used to control the game's frame rate.
            - 'font_big' : pygame.font.Font
                Font object used for large UI elements like "GAME OVER".
            - 'font_small' : pygame.font.Font
                Font object used for smaller instructions and hints.
            - 'road' : pygame.Surface
                The background image for the racing track.
            - 'cars' : list of pygame.Surface
                A collection of car sprites for obstacles.
            - 'trucks' : list of pygame.Surface
                A collection of truck sprites for obstacles.
            - 'explosion' : pygame.Surface
                The sprite used for the crash animation.
        """
        self.screen = assets["screen"]
        self.clock = assets["clock"]
        self.font_big = assets["font_big"]
        self.font_small = assets["font_small"]

        self.road_img = assets["road"]
        self.car_images = assets["cars"]
        self.truck_images = assets["trucks"]
        self.explosion_img = assets["explosion"]

        self.reset()

    # ----------------------------
    # RESET
    # ----------------------------
    def reset(self):
        """
        Reset the game state and reinitialize players and managers.

        Restores difficulty settings, clears existing obstacles, and
        repositions both players to their starting locations.

        Returns
        -------
        None
        """
        self.state = GameState()
        self.state.started = False
        self.state.paused = False

        self.road = Road(self.road_img)
        self.enemies = ObstacleManager(self.car_images, self.truck_images)

        player1_img = AssetManager.load_car(C.PLAYER1_COLOR)
        player2_img = AssetManager.load_car(C.PLAYER2_COLOR)

        player1_img = pg.transform.smoothscale(
            player1_img,
            (C.CAR_WIDTH, C.CAR_HEIGHT)
        )

        player2_img = pg.transform.smoothscale(
            player2_img,
            (C.CAR_WIDTH, C.CAR_HEIGHT)
        )

        self.player1 = PlayerCar(
            player1_img,
            pg.K_a,
            pg.K_d
        )

        self.player2 = PlayerCar(
            player2_img,
            pg.K_LEFT,
            pg.K_RIGHT
        )

        self.player1.rect.centerx = C.WIDTH // 3
        self.player2.rect.centerx = C.WIDTH * 2 // 3

    # ----------------------------
    # UPDATE
    # ----------------------------
    def update(self, keys, dt, now):
        """
        Update the game logic and object positions.

        Handles time-based difficulty scaling, player movement based on
        keyboard input, obstacle spawning, and movement of the road.

        Parameters
        ----------
        keys : pygame.key.ScancodeWrapper
            The state of all keyboard buttons.
        dt : int
            Time passed since the last frame in milliseconds.
        now : int
            Current time in milliseconds since pygame.init() was called.

        Returns
        -------
        None
        """
        dt_sec = dt / 1000
        self.state.time += dt_sec
        self.state.update_difficulty()

        self.player1.update(keys)
        self.player2.update(keys)

        self.player1.rect.x = max(
            0,
            min(self.player1.rect.x, C.WIDTH - self.player1.rect.width)
        )
        self.player2.rect.x = max(
            0,
            min(self.player2.rect.x, C.WIDTH - self.player2.rect.width)
        )

        self.road.update(dt_sec, self.state.speed)

        if now - self.state.last_spawn >= self.state.spawn_interval:
            self.enemies.spawn(
                self.state.max_enemies,
                self.state.speed
            )
            self.state.last_spawn = now

        self.enemies.update(dt_sec)
        self.check_collisions()

    # ----------------------------
    # COLLISIONS
    # ----------------------------
    def check_collisions(self):
        """
        Detect and resolve interactions between players and obstacles.

        Evaluates collisions between each player's hitbox and active
        obstacles, as well as head-on or side collisions between
        the two players.

        Returns
        -------
        None
            Triggers `handle_result` if a collision is detected.

        Notes
        -----
        Player-to-player collision logic uses the `direction` attribute
        to determine fault (e.g., which player swerved into the other).
        """
        crash1 = self.enemies.check_collision(self.player1.rect)
        crash2 = self.enemies.check_collision(self.player2.rect)

        if self.player1.rect.colliderect(self.player2.rect):

            # Player1 зліва врізається тільки рухаючись вправо
            if self.player1.direction == 1:
                self.handle_result(True, False)
                return

            # Player2 справа врізається тільки рухаючись вліво
            elif self.player2.direction == -1:
                self.handle_result(False, True)
                return

        if crash1 or crash2:
            self.handle_result(crash1, crash2)

    def show_explosion(self, crash1, crash2):
        """
        Render the explosion animation at the point of impact.

        Parameters
        ----------
        crash1 : bool
            True if Player 1 has collided.
        crash2 : bool
            True if Player 2 has collided.

        Returns
        -------
        None
        """
        self.road.draw(self.screen)
        self.enemies.draw(self.screen)
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)

        expl = pg.transform.smoothscale(self.explosion_img, (120, 120))
        if crash1:
            self.screen.blit(
                expl,
                expl.get_rect(center=self.player1.rect.center)
            )

        if crash2:
            self.screen.blit(
                expl,
                expl.get_rect(center=self.player2.rect.center)
            )

        pg.display.flip()
        pg.time.delay(700)

    def handle_result(self, crash1, crash2):
        """
        Determine the winner and initiate the game-over sequence.

        Parameters
        ----------
        crash1 : bool
            Indicates if Player 1 crashed.
        crash2 : bool
            Indicates if Player 2 crashed.

        Returns
        -------
        None
        """
        if crash1 and crash2:
            result_text = "DRAW!"

        elif crash1:
            result_text = "PLAYER 2 WINS!"

        else:
            result_text = "PLAYER 1 WINS!"

        self.show_explosion(crash1, crash2)
        self.show_game_over(result_text)
        self.wait_for_restart()
        self.reset()

    # ----------------------------
    # DRAW
    # ----------------------------
    def draw(self):
        """
        Render all game objects to the screen.

        Draws the road, obstacles, and players. Displays a start message
        if the game has not yet begun.

        Returns
        -------
        None
        """
        self.screen.fill(C.GRAY)
        self.road.draw(self.screen)
        self.enemies.draw(self.screen)

        self.player1.draw(self.screen)
        self.player2.draw(self.screen)

        if not self.state.started:
            text = self.font_big.render("Press SPACE to start", True, C.WHITE)
            rect = text.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2))
            self.screen.blit(text, rect)

        pg.display.flip()

    # ----------------------------
    # GAME OVER
    # ----------------------------
    def show_game_over(self, result_text):
        """
        Display the final results and restart instructions on the screen.

        Parameters
        ----------
        result_text : str
            The message indicating who won or if it was a draw.

        Returns
        -------
        None
        """
        cx, cy = C.WIDTH // 2, C.HEIGHT // 2

        game_over = self.font_big.render("GAME OVER", True, C.WHITE)
        self.screen.blit(game_over, game_over.get_rect(center=(cx, cy - 80)))

        result = self.font_big.render(result_text, True, C.YELLOW)
        self.screen.blit(result, result.get_rect(center=(cx, cy)))

        press = self.font_small.render("Press any key to restart", True, C.WHITE)
        self.screen.blit(press, press.get_rect(center=(cx, cy + 80)))

        pg.display.flip()

    def wait_for_restart(self):
        """
        Halt execution and wait for user input to restart.

        Returns
        -------
        None
        """
        waiting = True
        while waiting:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if e.type == pg.KEYDOWN:
                    waiting = False
            self.clock.tick(30)

    # ----------------------------
    # MAIN LOOP
    # ----------------------------
    def run(self):
        """
        Execute the main game loop for the two-player mode.

        This method handles the continuous cycle of event processing,
        physics/logic updates, and frame rendering until the user
        exits or the process is terminated.

        Parameters
        ----------
        None
            This method does not take external parameters as it uses
            the instance's internal state.

        Returns
        -------
        None
            The method returns only when the application is closed.

        Notes
        -----
        The loop uses `self.clock.tick(C.FPS)` to maintain a stable
        frame rate and calculates `dt` for frame-independent movement.
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
                        if not self.state.started:
                            self.state.started = True
                        else:
                            self.state.paused = not self.state.paused

                    elif e.key == pg.K_ESCAPE:
                        running = False

            keys = pg.key.get_pressed()

            if self.state.started and not self.state.paused:
                self.update(keys, dt, now)

            self.draw()

        pg.quit()
        sys.exit()