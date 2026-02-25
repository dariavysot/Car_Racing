# NOTE:
# This file defines the stable game skeleton.
# Other features should plug into update/draw/reset blocks.

import os
import sys
import pygame as pg
from storage.highscore import HighScore

from config import Settings as C
from state import GameState
from managers.asset_manager import AssetManager
from managers.obstacle_manager import ObstacleManager
from entities.road import Road
from entities.player import PlayerCar

class Game:
    def __init__(self):
        self.init_pygame()
        self.init_screen()
        self.init_fonts()
        self.load_assets()
        self.reset()
        self.highscore = HighScore()

    # ----------------------------
    # INIT BLOCK
    # ----------------------------
    def init_pygame(self):
        pg.init()
        self.clock = pg.time.Clock()

    def init_screen(self):
        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Car Racing")
        pg.display.set_icon(pg.image.load("images/icon.png"))

    def init_fonts(self):
        self.font_big = pg.font.SysFont("arial", 40, bold=True)
        self.font_small = pg.font.SysFont("arial", 24, bold=True)

    # ----------------------------
    # ASSETS BLOCK
    # ----------------------------
    def load_assets(self):
        am = AssetManager
        self.road_img = am.load_road()
        self.player_img = am.load_car(C.PLAYER_COLOR)
        self.explosion_img = am.load_explosion()
        self.player_img = pg.transform.smoothscale(self.player_img, (C.CAR_WIDTH, C.CAR_HEIGHT))
        self.car_images = []
        self.truck_images = []
        colors = ["red", "blue", "yellow", "orange", "purple", "green"]
        for color in colors:
            if color != C.PLAYER_COLOR:
                self.car_images.append(am.load_car(color))
        self.car_images.append(am.load_taxi())
        for num in range(2):
            self.truck_images.append(am.load_truck(num))


    # ----------------------------
    # RESET BLOCK
    # ----------------------------
    def reset(self):
        self.state = GameState()
        self.state.started = False
        self.state.paused = False
        self.reset_player()                 # Core & Player
        self.reset_enemies()                # Obstacles & Math
        self.reset_road()                   # Core & Player

    def reset_player(self):
        self.player = PlayerCar(self.player_img)

    def reset_enemies(self):
        self.enemies = ObstacleManager(self.car_images, self.truck_images)

    def reset_road(self):
        self.road = Road(self.road_img)

    # ----------------------------
    # UPDATE BLOCK
    # ----------------------------
    def update_objects(self, keys, dt, now):
        dt_sec = dt / 1000
        self.state.time += dt_sec
        self.player.update(keys)
        self.road.update(dt_sec, self.state.speed)
        self.state.update_difficulty()

        if now - self.state.last_spawn >= self.state.spawn_interval:
            self.enemies.spawn(
                self.state.max_enemies,
                self.state.speed
            )
            self.state.last_spawn = now

        self.enemies.update(dt_sec)

    def check_collisions(self):           # Logic & UI
        return self.enemies.check_collision(self.player.rect)

    # ----------------------------
    # DRAW BLOCK
    # ----------------------------
    def draw(self, dt):
        self.screen.fill(C.GRAY)
        self.road.draw(self.screen)
        self.enemies.draw(self.screen)    # Core & Player
        self.player.draw(self.screen)     # Core & Player
        self.draw_score(dt)               # Logic & UI

        if self.state.paused:
            paused_text = self.font_big.render("PAUSED", True, C.WHITE)
            rect = paused_text.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2))
            self.screen.blit(paused_text, rect)

        if not self.state.started:
            start_text = self.font_big.render("Press SPACE to start", True, C.WHITE)
            rect = start_text.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2))
            self.screen.blit(start_text, rect)

        pg.display.flip()  

    def draw_score(self, dt):
        score = self.font_small.render(
            f"Score: {int(self.state.time * 10)}", True, C.WHITE
        )

        # data = self.font_small.render(
        #     f"Spawn: {self.state.spawn_interval}", True, C.WHITE
        # )

        self.screen.blit(score, (10, 10))
        # self.screen.blit(data, (10, 30))

    # ----------------------------
    # CRASH BLOCK                         Logic & UI
    # ----------------------------
    def handle_crash(self, enemy_rect):
        self.show_explosion(enemy_rect)
        self.show_game_over()
        final_score = self.state.score // 100
        self.highscore.save_if_better(final_score)
        self.wait_for_restart()

    def show_explosion(self, enemy):
        mid = (
            (self.player.rect.centerx + enemy.rect.centerx) // 2,
            (self.player.rect.centery + enemy.rect.centery) // 2
        )

        self.road.draw(self.screen)
        self.enemies.draw(self.screen)
        self.player.draw(self.screen)

        expl = pg.transform.smoothscale(self.explosion_img, (120, 120))
        self.screen.blit(expl, expl.get_rect(center=mid))
        pg.display.flip()
        pg.time.delay(700)


    def show_game_over(self):
        game_over = self.font_big.render("GAME OVER", True, C.WHITE)
        press = self.font_small.render("Press any key to restart", True, C.WHITE)
        self.screen.blit(game_over, game_over.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 - 30)))
        self.screen.blit(press, press.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 + 20)))
        # --- High Score ---
        hs_text = self.font_small.render(
            f"High Score: {self.highscore.value}",
            True,
            C.YELLOW
        )

        self.screen.blit(
            hs_text,
            hs_text.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 + 60))
        )
        pg.display.flip()

    def wait_for_restart(self):
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
                self.update_objects(keys, dt, now)

                crashed = self.check_collisions()
                if crashed:
                    self.handle_crash(crashed)
                    self.reset()

            self.draw(dt)

        pg.quit()
        sys.exit()
