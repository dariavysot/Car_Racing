from unittest.mock import MagicMock, patch

import pygame as pg
import pytest

from config import Settings as C
from managers.obstacle_manager import ObstacleManager

pytestmark = [pytest.mark.obstacles]


@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch("managers.obstacle_manager.random") as mock_random, patch(
        "managers.obstacle_manager.pg"
    ) as mock_pg, patch(
        "managers.obstacle_manager.Obstacle"
    ) as mock_obstacle_class, patch(
        "managers.obstacle_manager.check_rect_collision"
    ) as mock_collision, patch(
        "managers.obstacle_manager.C"
    ) as mock_c:

        mock_c.LANES = 6
        mock_c.LANE_WIDTH = 80
        mock_c.WIDTH = 480
        mock_c.HEIGHT = 720
        mock_c.CAR_HEIGHT = 60
        mock_c.PLAYER_Y = 600
        mock_c.LANE_OFFSET = 40

        mock_random.randint.return_value = 3
        mock_random.sample.return_value = [1, 3, 5]
        mock_random.uniform.return_value = 0.6
        mock_random.choices.side_effect = (
            lambda population, weights=None, k=1: [population[0]] * k
        )

        yield {
            "random": mock_random,
            "pg": mock_pg,
            "Obstacle": mock_obstacle_class,
            "check_collision": mock_collision,
            "C": mock_c,
        }


@pytest.fixture
def mock_car_images():
    return [MagicMock(spec=pg.Surface) for _ in range(4)]


@pytest.fixture
def mock_truck_images():
    return [MagicMock(spec=pg.Surface) for _ in range(2)]


@pytest.fixture
def obstacle_manager(mock_dependencies, mock_car_images, mock_truck_images):
    manager = ObstacleManager(mock_car_images, mock_truck_images)
    manager._mocks = mock_dependencies
    return manager


@pytest.fixture
def mock_player_rect():
    rect = MagicMock(spec=pg.Rect)
    rect.centerx = 200
    rect.left = 150
    rect.right = 250
    return rect


@pytest.fixture
def mock_player_rects_two():
    left = MagicMock(spec=pg.Rect)
    left.centerx = 150
    left.left = 100
    left.right = 200

    right = MagicMock(spec=pg.Rect)
    right.centerx = 330
    right.left = 280
    right.right = 380

    return [left, right]


@pytest.mark.component
@pytest.mark.init
def test_init_sets_attributes(obstacle_manager, mock_car_images, mock_truck_images):
    assert obstacle_manager.car_images == mock_car_images
    assert obstacle_manager.track_images == mock_truck_images
    assert obstacle_manager.obstacles == []
    assert len(obstacle_manager.lane_speeds) == C.LANES
    assert obstacle_manager.images["CAR"] == mock_car_images
    assert obstacle_manager.images["TRUCK"] == mock_truck_images


@pytest.mark.unit
@pytest.mark.parametrize(
    "lane, expected", [(0, "SAME"), (1, "OPPOSITE"),
                       (2, "SAME"), (5, "OPPOSITE")]
)
def test_get_lane_type(obstacle_manager, lane, expected):
    assert obstacle_manager.get_lane_type(lane) == expected


@pytest.mark.unit
@pytest.mark.spawn
@pytest.mark.parametrize(
    "left_left, left_right, right_left, right_right, expected_trapped",
    [
        (100, 200, 280, 380, None),
        (20, 80, 130, 190, "left"),
        (270, 340, 390, 460, "right"),
    ],
    ids=["enough_space", "left_trapped", "right_trapped"],
)
def test_detect_trapped_player(
    obstacle_manager,
    left_left,
    left_right,
    right_left,
    right_right,
    expected_trapped,
    mock_player_rects_two,
):
    p_left = mock_player_rects_two[0]
    p_right = mock_player_rects_two[1]

    p_left.left = left_left
    p_left.right = left_right
    p_left.centerx = (left_left + left_right) // 2

    p_right.left = right_left
    p_right.right = right_right
    p_right.centerx = (right_left + right_right) // 2

    rects = [p_left, p_right]
    result = obstacle_manager.detect_trapped_player(rects)

    if expected_trapped is None:
        assert result is None
    elif expected_trapped == "left":
        assert result is p_left
    else:
        assert result is p_right


@pytest.mark.unit
@pytest.mark.spawn
def test_escape_exists_returns_true_when_path_exists(obstacle_manager):
    obs = MagicMock()
    obs.lane = 2
    obs.rect = MagicMock(y=100)
    obs.speed = 100

    assert obstacle_manager.escape_exists(2, 0, 5, [obs]) is True


@pytest.mark.unit
@pytest.mark.spawn
def test_escape_exists_returns_false_when_fully_blocked(obstacle_manager):
    obstacles = []
    for lane in range(C.LANES):
        obs = MagicMock()
        obs.lane = lane
        obs.rect = MagicMock(y=C.PLAYER_Y - 30)
        obs.speed = 0
        obstacles.append(obs)

    assert obstacle_manager.escape_exists(0, 0, 5, obstacles) is False


@pytest.mark.component
@pytest.mark.spawn
def test_is_spawn_safe_single_player(obstacle_manager, mock_player_rect):
    obstacle_manager.escape_exists = MagicMock(return_value=True)
    assert obstacle_manager.is_spawn_safe(
        [MagicMock()], [mock_player_rect]) is True


@pytest.mark.component
@pytest.mark.spawn
def test_is_spawn_safe_two_players_both_safe(obstacle_manager, mock_player_rects_two):
    obstacle_manager.escape_exists = MagicMock(return_value=True)
    obstacle_manager.detect_trapped_player = MagicMock(return_value=None)

    assert obstacle_manager.is_spawn_safe(
        [MagicMock()], mock_player_rects_two) is True
    assert obstacle_manager.escape_exists.call_count == 2


@pytest.mark.component
@pytest.mark.spawn
def test_is_spawn_safe_two_players_trapped(obstacle_manager, mock_player_rects_two):
    trapped = mock_player_rects_two[0]
    obstacle_manager.detect_trapped_player = MagicMock(return_value=trapped)
    obstacle_manager.escape_exists = MagicMock(return_value=True)

    assert obstacle_manager.is_spawn_safe(
        [MagicMock()], mock_player_rects_two) is True


@pytest.mark.component
@pytest.mark.spawn
def test_spawn_creates_obstacles_when_safe(
    obstacle_manager, mock_player_rect, mock_dependencies
):
    obstacle_manager.is_spawn_safe = MagicMock(return_value=True)
    obstacle_manager.get_lane_type = MagicMock(return_value="SAME")

    obstacle_manager.spawn(max_enemies=0.8, player_rects=[mock_player_rect])

    assert len(obstacle_manager.obstacles) >= 1
    obstacle_manager.is_spawn_safe.assert_called_once()


@pytest.mark.component
@pytest.mark.spawn
def test_spawn_respects_trapped_player_safe_lane(
    obstacle_manager, mock_player_rects_two
):
    obstacle_manager.detect_trapped_player = MagicMock(
        return_value=mock_player_rects_two[0]
    )
    obstacle_manager.is_spawn_safe = MagicMock(return_value=True)

    obstacle_manager.spawn(max_enemies=1.0, player_rects=mock_player_rects_two)

    assert len(obstacle_manager.obstacles) > 0


@pytest.mark.component
@pytest.mark.update
def test_update_moves_and_cleans_obstacles(obstacle_manager):
    o1 = MagicMock()
    o1.is_out.return_value = False
    o1.lane = 2
    o1.speed = 120

    o2 = MagicMock()
    o2.is_out.return_value = True

    obstacle_manager.obstacles = [o1, o2]
    obstacle_manager.update(dt_sec=0.016)

    o1.update.assert_called_once_with(0.016)
    assert len(obstacle_manager.obstacles) == 1
    assert obstacle_manager.lane_speeds[2] == [120]


@pytest.mark.component
@pytest.mark.collision
def test_check_collision_returns_obstacle_or_none(obstacle_manager, mock_dependencies):
    o1 = MagicMock()
    o2 = MagicMock()
    obstacle_manager.obstacles = [o1, o2]

    mock_dependencies["check_collision"].side_effect = [False, True]

    result = obstacle_manager.check_collision(MagicMock())
    assert result is o2


@pytest.mark.component
def test_draw_calls_obstacle_methods(obstacle_manager, mock_dependencies):
    o1 = MagicMock()
    o2 = MagicMock()
    obstacle_manager.obstacles = [o1, o2]
    screen = MagicMock(spec=pg.Surface)

    obstacle_manager.draw(screen, is_night=True)

    o1.draw.assert_called_once_with(screen)
    o1.draw_only_light.assert_called_once_with(screen, True)
    o2.draw.assert_called_once_with(screen)
    o2.draw_only_light.assert_called_once_with(screen, True)
