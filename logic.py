import os, sys
import pygame as pg

from config import Settings as C
from state import GameState
from managers.asset_manager import AssetManager
from managers.obstacle_manager import ObstacleManager
from entities.road import Road
from entities.player import Player

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Car Racing")
        pg.display.set_icon(pg.image.load("images/icon.png"))

        self.clock = pg.time.Clock()
        self.font_big = pg.font.SysFont("arial", 40, bold=True)
        self.font_small = pg.font.SysFont("arial", 24, bold=True)

        self.load_assets()
        self.reset()

    def load_assets(self):
        am = AssetManager

        road = am.load_sprite("images/road.png", am.make_road_fallback)
        ratio = road.get_height() / road.get_width()
        self.road_img = pg.transform.smoothscale(
            road, (C.WIDTH, int(C.WIDTH * ratio))
        )

        self.car_w = C.WIDTH // 4.4
        self.car_h = int(self.car_w * 1.4)

        self.player_img = pg.transform.smoothscale(
            am.load_sprite("images/player.png", lambda: am.make_car_fallback(C.RED)),
            (self.car_w, self.car_h)
        )

        self.enemy_img = pg.transform.smoothscale(
            am.load_sprite("images/player.png", lambda: am.make_car_fallback(C.BLUE)),
            (self.car_w, self.car_h)
        )

        self.explosion_img = am.load_sprite(
            "images/explosion.png", am.make_explosion_fallback
        )

    def reset(self):
        self.state = GameState()
        self.player = Player(self.player_img, self.car_w)
        self.enemies = ObstacleManager(self.enemy_img, self.car_w, self.car_h)
        self.road = Road(self.road_img)

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(C.FPS)
            now = pg.time.get_ticks()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    running = False

            keys = pg.key.get_pressed()

            self.player.update(keys)
            self.road.update()

            if now - self.state.last_spawn >= C.SPAWN_INTERVAL:
                self.enemies.spawn()
                self.state.last_spawn = now

            self.enemies.update()
            crashed = self.enemies.check_collision(self.player.rect)

            self.draw(dt)

            if crashed:
                self.handle_crash(crashed)
                self.reset()

        pg.quit()
        sys.exit()

    def draw(self, dt):
        self.screen.fill(C.GRAY)
        self.road.draw(self.screen)
        self.enemies.draw(self.screen)
        self.player.draw(self.screen)

        self.state.score += dt
        self.state.difficulty += dt * 0.002 / 1000

        score = self.font_small.render(
            f"Score: {self.state.score // 100}", True, C.WHITE
        )
        self.screen.blit(score, (10, 10))
        pg.display.flip()

    def handle_crash(self, enemy_rect):
        mid = (
            (self.player.rect.centerx + enemy_rect.centerx) // 2,
            (self.player.rect.centery + enemy_rect.centery) // 2
        )

        expl = pg.transform.smoothscale(self.explosion_img, (120, 120))
        self.screen.blit(expl, expl.get_rect(center=mid))
        pg.display.flip()
        pg.time.delay(700)

        game_over = self.font_big.render("GAME OVER", True, C.WHITE)
        press = self.font_small.render("Press any key to restart", True, C.WHITE)

        self.screen.blit(
            game_over, game_over.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 - 30))
        )
        self.screen.blit(
            press, press.get_rect(center=(C.WIDTH // 2, C.HEIGHT // 2 + 20))
        )
        pg.display.flip()

        waiting = True
        while waiting:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if e.type == pg.KEYDOWN:
                    waiting = False
            self.clock.tick(30)