import random
import pygame as pg
from config import Settings as C
from gameplay.collision import check_rect_collision
from entities.obstacle import Obstacle


class TrafficType:
    """
    Constants for traffic direction types.
    """
    SAME = "SAME"
    OPPOSITE = "OPPOSITE"


class ObstacleManager:
    """
    Manages spawning, movement, and collision logic for all road obstacles.

    Parameters
    ----------
    car_images : list of pg.Surface
        Collection of textures for standard cars.
    track_images : list of pg.Surface
        Collection of textures for trucks/larger vehicles.

    Attributes
    ----------
    obstacles : list of Obstacle
        Active obstacles currently in the game world.
    lane_speeds : list of lists
        Current speeds of obstacles indexed by lane.
    images : dict
        Mapping of obstacle types to their respective image lists.
    speed_groups : dict
        Speed multipliers based on TrafficType.
    """

    def __init__(self, car_images, track_images):
        self.car_images = car_images
        self.track_images = track_images

        self.obstacles = []

        self.horizon = 3.0
        self.sim_dt = 0.01

        self.lane_speeds = [[] for _ in range(C.LANES)]

        self.images = {}
        self.images["CAR"] = self.car_images
        self.images["TRUCK"] = self.track_images

        self.speed_groups = {
            TrafficType.SAME: (0.5, 0.75),      # 50–75 %
            TrafficType.OPPOSITE: (1.25, 1.5)   # 125–150 %
        }

    def get_lane_type(self, lane):
        """
        Determine if a lane is following or opposing player direction.

        Parameters
        ----------
        lane : int
            The lane index.

        Returns
        -------
        str
            TrafficType.SAME or TrafficType.OPPOSITE.
        """
        if lane % 2 == 0:
            return TrafficType.SAME
        return TrafficType.OPPOSITE
<<<<<<< HEAD

    def is_spawn_safe(self, candidates, base_speed):
=======
>>>>>>> feature/math

    def is_spawn_safe(self, candidates, base_speed, player_x):
        """
        Run a look-ahead simulation to ensure a spawn configuration is escapable.

        Parameters
        ----------
        candidates : list of Obstacle
            Proposed obstacles to spawn.
        base_speed : float
            Current global game speed.
        player_x : float
            Current horizontal position of the player.

        Returns
        -------
        bool
            True if a safe path exists through the obstacles, False otherwise.
        """
        player_lane = int((player_x - C.LANE_OFFSET) / C.LANE_WIDTH)
        sim_obstacles = self.obstacles + candidates
        reachable_min = reachable_max = player_lane
        t = 0.0
        dt = 0.04
        horizon = 2.8

        while t < horizon:
            max_shift = t * C.PLAYER_LANE_SPEED
            cur_min = max(0, reachable_min - max_shift)
            cur_max = min(C.LANES - 1, reachable_max + max_shift)

            blocked = set()
            for o in sim_obstacles:
                future_y = o.rect.y + o.speed * t
                if abs(future_y - C.PLAYER_Y) < C.CAR_HEIGHT * 1.2:
                    blocked.add(o.lane)

            safe_lanes = [lane for lane in range(C.LANES)
                        if lane not in blocked and cur_min <= lane <= cur_max]

            if not safe_lanes:
                return False

            reachable_min = min(safe_lanes)
            reachable_max = max(safe_lanes)
            t += dt
        return True

    def spawn(self, max_enemies, player_x, base_speed=None):
        """
        Attempt to generate a new wave of obstacles based on difficulty metrics.

        Parameters
        ----------
        max_enemies : float
            Difficulty factor determining potential obstacle density.
        player_x : float
            Player's current X position for safety verification.
        base_speed : float, optional
            The reference speed for scaling obstacle movement.
        """
        if base_speed is None:
            base_speed = 360

        attempts = 0
        while attempts < 25:
            obstacle_count = random.randint(
                1,
                max(1, int(C.LANES * max_enemies))
            )
            lanes = random.sample(range(C.LANES), obstacle_count)

            candidates = []
            for lane in lanes:
<<<<<<< HEAD

=======
>>>>>>> feature/math
                lane_type = self.get_lane_type(lane)
                mult_min, mult_max = self.speed_groups[lane_type]
                speed = base_speed * random.uniform(mult_min, mult_max)

                if self.lane_speeds[lane]:
                    speed = min(speed, min(self.lane_speeds[lane]))

                obstacle_type = random.choices(["CAR", "TRUCK"], [0.75, 0.25], k=1)[0]
                image = random.choices(self.images[obstacle_type], k=1)[0]
                if lane_type == TrafficType.OPPOSITE:
                    image = pg.transform.flip(image, False, True)

                obstacle = Obstacle(
                    image,
                    lane,
                    - C.HEIGHT / 2,
                    speed,
                    direction=lane_type
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
        """
        Advance all obstacles and remove those out of bounds.

        Parameters
        ----------
        dt_sec : float
            The time elapsed since the last frame in seconds (delta time).
        """
        for o in self.obstacles:
            o.update(dt_sec)

        self.obstacles = [
            o for o in self.obstacles
            if not o.is_out()
        ]

        self.lane_speeds = [[] for _ in range(C.LANES)]
        for o in self.obstacles:
<<<<<<< HEAD
=======
            self.lane_speeds[o.lane].append(o.speed)

    def check_collision(self, player_rect):
        """
        Check if any active obstacle intersects with the player's rect.

        Parameters
        ----------
        player_rect : pg.Rect
            The player's hitbox.

        Returns
        -------
        Obstacle or None
            The obstacle involved in collision, or None if no collision.
        """
        for o in self.obstacles:
>>>>>>> feature/math
            if check_rect_collision(player_rect, o.rect):
                return o
        return None

    def draw(self, screen, is_night):
<<<<<<< HEAD
        """Render lighting effects for all managed obstacles."""
        for o in self.obstacles:
            o.draw_only_light(screen, is_night)
=======
        """
        Render all obstacles to the given surface.

        Parameters
        ----------
        screen : pg.Surface
            The game display surface.
        """
        for o in self.obstacles:
            o.draw(screen)
            o.draw_only_light(screen, is_night)
>>>>>>> feature/math
