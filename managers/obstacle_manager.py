import random
import pygame as pg
from config import Settings as C
from entities.obstacle import Obstacle


class TrafficType:
    SAME = "SAME"
    OPPOSITE = "OPPOSITE"


class ObstacleManager:

    def __init__(self, car_images, track_images):
        self.car_images = car_images
        self.track_images = track_images

        self.obstacles = []

        self.horizon = 3.0
        self.sim_dt = 0.01

        self.images = {}
        self.images["CAR"] = self.car_images
        self.images["TRUCK"] = self.track_images

        self.speed_groups = {
            TrafficType.SAME: (0.5, 0.75),      # 50–75 %
            TrafficType.OPPOSITE: (1.25, 1.5)   # 125–150 %
        }

    def get_lane_type(self, lane):
        if lane % 2 == 0:
            return TrafficType.SAME
        return TrafficType.OPPOSITE


    def is_spawn_safe(self, candidates, base_speed, player_x):
        player_lane = int((player_x - C.LANE_OFFSET) / C.LANE_WIDTH)
        sim_obstacles = self.obstacles + candidates
        reachable_min = player_lane
        reachable_max = player_lane

        t = 0.0
        while t < self.horizon:
            max_shift = t * C.PLAYER_LANE_SPEED

            cur_min = max(0, reachable_min - max_shift)
            cur_max = min(C.LANES - 1, reachable_max + max_shift)

            blocked_lanes = set()
            for o in sim_obstacles:
                future_y = o.rect.y + o.speed * t
                if abs(future_y - C.PLAYER_Y) < C.CAR_HEIGHT:
                    blocked_lanes.add(o.lane)

            safe_lanes = [
                lane for lane in range(C.LANES)
                if lane not in blocked_lanes
                and cur_min <= lane <= cur_max
            ]

            if not safe_lanes:
                return False

            reachable_min = min(safe_lanes)
            reachable_max = max(safe_lanes)

            t += self.sim_dt

        return True

    def spawn(self, max_enemies, player_x, base_speed=None):
        if base_speed is None:
            base_speed = 360

        attempts = 0
        while attempts < 40:
            obstacle_count = random.randint(
                1,
                max(1, int(C.LANES * max_enemies))
            )
            lanes = random.sample(range(C.LANES), obstacle_count)

            candidates = []
            for lane in lanes:
                lane_type = self.get_lane_type(lane)
                mult_min, mult_max = self.speed_groups[lane_type]
                speed = base_speed * random.uniform(mult_min, mult_max)

                ahead_obstacles = [o for o in self.obstacles if o.lane == lane]
                if ahead_obstacles:
                    min_ahead_speed = min(o.speed for o in ahead_obstacles)
                    speed = min(speed, min_ahead_speed)

                obstacle_type = random.choices(["CAR", "TRUCK"], [0.75, 0.25], k=1)[0]
                image = random.choices(self.images[obstacle_type], k=1)[0]
                if lane_type == TrafficType.OPPOSITE:
                    image = pg.transform.flip(image, False, True)

                obstacle = Obstacle(
                    image,
                    lane,
                    -C.HEIGHT / 2,
                    speed
                )
                candidates.append(obstacle)

            spawn_y = -C.HEIGHT / 2
            immediate_safe = not any(
                c.lane == o.lane and abs(c.rect.y - o.rect.y) < C.CAR_HEIGHT * 1.5
                for c in candidates
                for o in self.obstacles
            )

            if not immediate_safe:
                attempts += 1
                continue

            if self.is_spawn_safe(candidates, base_speed, player_x):
                self.obstacles.extend(candidates)
                return

            attempts += 1

    def update(self, dt_sec):
        for o in self.obstacles:
            o.update(dt_sec)

        self.obstacles = [
            o for o in self.obstacles
            if not o.is_out()
        ]

    def check_collision(self, player_rect):
        for o in self.obstacles:
            if o.collides(player_rect):
                return o
        return None

    def draw(self, screen):
        for o in self.obstacles:
            o.draw(screen)