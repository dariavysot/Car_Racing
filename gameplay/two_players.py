import pygame as pg
import sys

from config import Settings as C
from state import GameState
from managers.obstacle_manager import ObstacleManager
from entities.road import Road
from entities.player import PlayerCar
from managers.asset_manager import AssetManager


class TwoPlayersGame:
    def __init__(self, assets):
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
        cx, cy = C.WIDTH // 2, C.HEIGHT // 2

        game_over = self.font_big.render("GAME OVER", True, C.WHITE)
        self.screen.blit(game_over, game_over.get_rect(center=(cx, cy - 80)))

        result = self.font_big.render(result_text, True, C.YELLOW)
        self.screen.blit(result, result.get_rect(center=(cx, cy)))

        press = self.font_small.render("Press any key to restart", True, C.WHITE)
        self.screen.blit(press, press.get_rect(center=(cx, cy + 80)))

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