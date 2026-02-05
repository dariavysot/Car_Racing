# NOTE:
# This file defines the stable game skeleton.
# Other features should plug into update/draw/reset blocks.

import os
import sys
import pygame as pg

from config import Settings as C
from state import GameState
from managers.asset_manager import AssetManager
from managers.obstacle_manager import ObstacleManager
from entities.road import Road
from entities.player import Player

class Game:
    def __init__(self):
        self.init_pygame()
        self.init_screen()
        self.init_fonts()
        self.load_assets()
        self.reset()

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
        self.player_img = am.load_player(C.RED)
        self.enemy_img = am.load_player(C.BLUE)
        self.explosion_img = am.load_explosion()

        self.car_w = C.WIDTH // 4.4
        self.car_h = int(self.car_w * 1.4)

    # ----------------------------
    # RESET BLOCK
    # ----------------------------
    def reset(self):
        self.state = GameState()
        self.reset_player()
        self.reset_enemies()
        self.reset_road()

    def reset_player(self):
        self.player = Player(self.player_img, self.car_w)

    def reset_enemies(self):
        self.enemies = ObstacleManager(self.enemy_img, self.car_w, self.car_h)

    def reset_road(self):
        self.road = Road(self.road_img)

    # ----------------------------
    # UPDATE BLOCK
    # ----------------------------
    def update_objects(self, keys, dt, now):
        self.player.update(keys)          # Core & Player
        self.road.update()                # Core & Player

        if now - self.state.last_spawn >= C.SPAWN_INTERVAL:
            self.enemies.spawn()          # Obstacles & Math
            self.state.last_spawn = now

        self.enemies.update()             # Obstacles & Math

    def check_collisions(self):
        return self.enemies.check_collision(self.player.rect)

    # ----------------------------
    # DRAW BLOCK
    # ----------------------------
    def draw(self, dt):
        self.screen.fill(C.GRAY)
        self.road.draw(self.screen)
        self.enemies.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_score(dt)

    def draw_score(self, dt):
        self.state.score += dt
        self.state.difficulty += dt * 0.002 / 1000

        score = self.font_small.render(
            f"Score: {self.state.score // 100}", True, C.WHITE
        )
        self.screen.blit(score, (10, 10))
        pg.display.flip()

    # ----------------------------
    # CRASH BLOCK
    # ----------------------------
    def handle_crash(self, enemy_rect):
        self.show_explosion(enemy_rect)
        self.show_game_over()
        self.wait_for_restart()

    def show_explosion(self, enemy_rect):
        mid = (
            (self.player.rect.centerx + enemy_rect.centerx) // 2,
            (self.player.rect.centery + enemy_rect.centery) // 2
        )

        self.screen.fill(C.GRAY)
        expl = pg.transform.smoothscale(self.explosion_img, (120, 120))
        self.screen.blit(expl, expl.get_rect(center=mid))
        pg.display.flip()
        pg.time.delay(700)


    def show_game_over(self):
        game_over = self.font_big.render("GAME OVER", True, C.WHITE)
        press = self.font_small.render("Press any key to restart", True, C.WHITE)
        self.screen.blit(game_over, game_over.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 - 30)))
        self.screen.blit(press, press.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 + 20)))
        pg.display.flip()

    def wait_for_restart(self):
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
        running = True
        while running:
            dt = self.clock.tick(C.FPS)
            now = pg.time.get_ticks()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    running = False

            keys = pg.key.get_pressed()
            self.update_objects(keys, dt, now)
            crashed = self.check_collisions()
            self.draw(dt)

            if crashed:
                self.handle_crash(crashed)
                self.reset()

        pg.quit()
        sys.exit()
