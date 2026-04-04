import pytest
from unittest.mock import patch, MagicMock
import pygame as pg
import math

from config import Settings as C
from entities.player import PlayerCar
from entities.obstacle import Obstacle


@pytest.fixture
def mock_image():
    real_width = C.CAR_WIDTH
    real_height = C.CAR_HEIGHT

    fake_surface = pg.Surface((real_width, real_height))

    mock_surf = MagicMock(spec=pg.Surface)
    mock_surf.convert_alpha.return_value = fake_surface

    def get_rect_side_effect(**kwargs):
        rect = fake_surface.get_rect()
        if 'center' in kwargs:
            rect.center = kwargs['center']
        elif 'centerx' in kwargs and 'centery' in kwargs:
            rect.center = (kwargs['centerx'], kwargs['centery'])
        return rect

    mock_surf.get_rect.side_effect = get_rect_side_effect

    return mock_surf


@pytest.fixture
def mock_screen():
    return MagicMock(spec=pg.Surface)


class TestPlayerCar:

    def test_init(self, mock_image):
        """PlayerCar.__init__"""
        car = PlayerCar(mock_image)

        assert car.image == mock_image
        assert car.rect.center == (C.WIDTH // 2, C.PLAYER_Y)
        assert car.speed == C.PLAYER_LANE_SPEED
        assert car.left_key == pg.K_LEFT
        assert car.right_key == pg.K_RIGHT
        assert car.direction == 0

    def test_update(self, mock_image):
        """PlayerCar.update"""
        car = PlayerCar(mock_image)
        dt_sec = 1.0

        # Move left
        keys = MagicMock()
        keys.__getitem__.side_effect = lambda k: True if k == pg.K_LEFT else False
        initial_x = car.rect.x
        car.update(keys, dt_sec)
        expected_x = initial_x - car.speed * dt_sec
        assert car.rect.x == max(0, expected_x)
        assert car.direction == -1

        # Move right
        car.rect.centerx = C.WIDTH // 2
        initial_x = car.rect.x
        keys.__getitem__.side_effect = lambda k: True if k == pg.K_RIGHT else False
        car.update(keys, dt_sec)
        expected_x = initial_x + car.speed * dt_sec
        assert car.rect.x == min(expected_x, C.WIDTH - car.rect.width)
        assert car.direction == 1

        # Right bound
        car.rect.x = C.WIDTH - 10
        car.update(keys, dt_sec)
        assert car.rect.x == C.WIDTH - car.rect.width

    def test_draw(self, mock_image, mock_screen):
        """PlayerCar.draw"""
        car = PlayerCar(mock_image)
        car.draw(mock_screen)
        mock_screen.blit.assert_called_once_with(car.image, car.rect)

    def test_draw_only_light(self, mock_image, mock_screen):
        """PlayerCar.draw_only_light"""
        car = PlayerCar(mock_image)

        with patch.object(car, "draw_lights") as mocked_draw_lights:
            car.draw_only_light(mock_screen, True)
            mocked_draw_lights.assert_called_once_with(mock_screen, True, direction="SAME")

        with patch.object(car, "draw_lights") as mocked_draw_lights:
            car.draw_only_light(mock_screen, False)
            mocked_draw_lights.assert_called_once_with(mock_screen, False, direction="SAME")


class TestObstacle:

    def test_init(self, mock_image):
        """Obstacle.__init__"""
        lane = 1
        y = 150.0
        speed = 250.0
        direction = "OPPOSITE"

        obs = Obstacle(mock_image, lane, y, speed, direction)

        assert obs.lane == lane
        assert obs.speed == speed
        assert obs.direction == direction

        expected_x = C.LANE_WIDTH * lane + C.LANE_OFFSET
        assert obs.rect.centerx == expected_x
        assert math.isclose(obs.rect.centery, y, abs_tol=0.01)

    def test_update(self, mock_image):
        """Obstacle.update"""
        obs = Obstacle(mock_image, 0, 100.0, 300.0)
        dt_sec = 0.016

        initial_y = obs.rect.y
        obs.update(dt_sec)

        expected_y = initial_y + obs.speed * dt_sec
        assert math.isclose(obs.rect.y, expected_y, abs_tol=0.25)

    def test_is_out(self, mock_image):
        """Obstacle.is_out"""
        obs = Obstacle(mock_image, 0, 0, 100)

        assert not obs.is_out()

        obs.rect.y = C.HEIGHT + C.CAR_HEIGHT + C.LIGHT_HEIGHT
        assert obs.is_out()

        obs.rect.y -= 1
        assert not obs.is_out()

    def test_collides(self, mock_image):
        """Obstacle.collides"""
        obs = Obstacle(mock_image, 0, 100, 100)
        player_rect = obs.rect.copy()

        assert obs.collides(player_rect)

        player_rect.move_ip(obs.rect.width + 10, 0)
        assert not obs.collides(player_rect)

    def test_draw(self, mock_image, mock_screen):
        """Obstacle.draw"""
        obs = Obstacle(mock_image, 0, 0, 100)
        obs.draw(mock_screen)
        mock_screen.blit.assert_called_once_with(obs.image, obs.rect)

    def test_draw_only_light(self, mock_image, mock_screen):
        """Obstacle.draw_only_light"""
        obs = Obstacle(mock_image, 0, 0, 100, direction="SAME")

        with patch.object(obs, "draw_lights") as mocked:
            obs.draw_only_light(mock_screen, True)
            mocked.assert_called_once_with(mock_screen, True, obs.direction)

        with patch.object(obs, "draw_lights") as mocked:
            obs.draw_only_light(mock_screen, False)
            mocked.assert_called_once_with(mock_screen, False, obs.direction)