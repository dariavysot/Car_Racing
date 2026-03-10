"""
Two-player competitive mode for the Car Racing game.

This module provides the `TwoPlayersGame` class, which manages a separate
game loop where two players can race simultaneously on the same screen,
avoiding obstacles and competing for survival.
"""

import pygame as pg
import sys

from logic import Game
from config import Settings as C
from state import GameState
from managers.obstacle_manager import ObstacleManager
from entities.road import Road
from entities.player import PlayerCar
from managers.asset_manager import AssetManager
from managers.theme_manager import ThemeManager
from managers.sound_manager import SoundManager


class TwoPlayersGame(Game):
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
    theme : ThemeManager
        Handles the day/night cycle transitions and dark overlay effects.
    """

    # ----------------------------
    # RESET
    # ----------------------------

    def reset_players(self):
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
            left_key=pg.K_a,
            right_key=pg.K_d
        )

        self.player2 = PlayerCar(
            player2_img,
            left_key=pg.K_LEFT,
            right_key=pg.K_RIGHT
        )

        self.player1.rect.centerx = C.WIDTH // 3
        self.player2.rect.centerx = C.WIDTH * 2 // 3

    # ----------------------------
    # UPDATE
    # ----------------------------
    def update_players(self, keys, dt_sec):
        self.player1.update(keys, dt_sec)
        self.player2.update(keys, dt_sec)

        self.player1.rect.x = max(
            0,
            min(self.player1.rect.x, C.WIDTH - self.player1.rect.width)
        )

        self.player2.rect.x = max(
            0,
            min(self.player2.rect.x, C.WIDTH - self.player2.rect.width)
        )

    # ----------------------------
    # COLLISIONS
    # ----------------------------

    def get_player_rects(self):
        return [
            self.player1.rect,
            self.player2.rect
        ]

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
        if self.player1.rect.colliderect(self.player2.rect):
            if self.player1.direction == 1:
                self.handle_result(True, False)
            elif self.player2.direction == -1:
                self.handle_result(False, True)
            else:
                self.handle_result(True, True)
            return None
        
        crash1 = self.enemies.check_collision(self.player1.rect)
        crash2 = self.enemies.check_collision(self.player2.rect)

        if crash1 or crash2:
            self.handle_result(bool(crash1), bool(crash2))
            return None

        return None

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

        self.theme.apply(self.screen)

        self.draw_players()

        self.enemies.draw(self.screen, self.theme.is_night)

        self.draw_player_lights()

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
        self.sounds.crash()
        self.sounds.pause()

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
    def draw_players(self):
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)

    def draw_player_lights(self):
        self.player1.draw_only_light(self.screen, self.theme.is_night)
        self.player2.draw_only_light(self.screen, self.theme.is_night)

    def show_game_over(self, result_text):
        """ Display the final results and restart instructions on the screen.
        
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