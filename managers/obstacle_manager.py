import random
from config import Settings as C
from entities.obstacle import Obstacle


class ObstacleManager:

    def __init__(self, image):
        self.image = image
        self.obstacles = []

        self.reachable_min = 0
        self.reachable_max = C.LANES - 1

        self.horizon = 2.0
        self.sim_dt = 0.05
    
    def is_spawn_safe(self, candidates, base_speed):

        sim_obstacles = self.obstacles + candidates

        reachable_min = self.reachable_min
        reachable_max = self.reachable_max

        t = 0.0

        while t < self.horizon:

            max_shift = t * 6

            cur_min = max(0, reachable_min - max_shift)
            cur_max = min(C.LANES - 1, reachable_max + max_shift)

            blocked_lanes = set()

            for o in sim_obstacles:
                speed_px_sec = o.speed * C.FPS
                future_y = o.rect.y + speed_px_sec * t

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

    def spawn(self, max_enemies, base_speed=None):

        if base_speed is None:
            base_speed = 6

        attempts = 0

        while attempts < 40:

            obstacle_count = random.randint(
                1,
                max(1, int(C.LANES * max_enemies))
            )

            lanes = random.sample(range(C.LANES), obstacle_count)

            candidates = []

            for lane in lanes:
                speed_variation = random.uniform(0.75, 1.25)
                speed = base_speed * speed_variation

                obstacle = Obstacle(
                    self.image,
                    lane,
                    - C.HEIGHT / 4,
                    speed
                )
                candidates.append(obstacle)

            if self.is_spawn_safe(candidates, base_speed):
                self.obstacles.extend(candidates)
                return

            attempts += 1

    def update(self, base_speed, dt_sec):

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