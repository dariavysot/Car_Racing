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
            TrafficType.SAME: (0.5, 0.75),  # 50–75 %
            TrafficType.OPPOSITE: (1.25, 1.5)  # 125–150 %
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

    def detect_trapped_player(self, player_rects):
        """
        Identify if one of the players is physically sandwiched between another player 
        and the road edge or between players with insufficient gap to maneuver.

        This check is specifically designed for 2-player mode to prevent 
        "impossible" spawn scenarios where players block each other's escape paths.

        Parameters
        ----------
        player_rects : list of pg.Rect
            A list containing the collision rectangles of the active players. 
            Expected length is 2 for this logic to trigger.

        Returns
        -------
        pg.Rect or None
            The rect of the player who is considered 'trapped' and needs 
            priority in safety calculations. Returns None if no player 
            is trapped or if there is only one player.
        """
        if len(player_rects) < 2:
            return None

        p_left, p_right = sorted(player_rects, key=lambda r: r.centerx)
        left_gap = p_left.left
        right_gap = C.WIDTH - p_right.right
        middle_gap = p_right.left - p_left.right
        lane_px = C.LANE_WIDTH

        if left_gap < lane_px * 0.5 and middle_gap < lane_px * 0.7:
            return p_left
        if right_gap < lane_px * 0.5 and middle_gap < lane_px * 0.7:
            return p_right

        return None

    def escape_exists(self, start_lane, min_lane, max_lane, sim_obstacles):
        """
        Evaluate if a viable path exists from a starting lane within a 
        given lane range over a temporal horizon.

        Uses a breadth-first search (BFS) approach over a simulated time 
        horizon to determine if a player can maneuver around obstacles 
        without a collision.

        Parameters
        ----------
        start_lane : int
            The index of the lane where the player is currently located.
        min_lane : int
            The leftmost lane index available for maneuvers (e.g., 0 for full road 
            or the start of a player's half-road).
        max_lane : int
            The rightmost lane index available for maneuvers (e.g., C.LANES - 1).
        sim_obstacles : list of Obstacle
            The collection of obstacles (existing and proposed) to include 
            in the pathfinding simulation.

        Returns
        -------
        bool
            True if there is at least one sequence of lane shifts (left, right, 
            or stay) that avoids all obstacles over the simulation horizon; 
            False otherwise.
        """
        dt = 0.05
        horizon = 3.0
        steps = int(horizon / dt)

        blocked_at_t = []

        for i in range(steps):

            t = i * dt
            blocked = set()

            for o in sim_obstacles:

                future_y = o.rect.y + o.speed * t

                if abs(future_y - C.PLAYER_Y) < C.CAR_HEIGHT * 1.25:
                    blocked.add(o.lane)

            blocked_at_t.append(blocked)

        reachable = {start_lane}

        for i in range(steps):

            blocked = blocked_at_t[i]
            new_reachable = set()

            for lane in reachable:

                for shift in (-1, 0, 1):

                    nl = lane + shift

                    if nl < min_lane or nl > max_lane:
                        continue

                    if nl in blocked:
                        continue

                    new_reachable.add(nl)

            if not new_reachable:
                return False

            reachable = new_reachable

        return True

    def is_spawn_safe(self, candidates, player_rects):
        """
        Run a look-ahead simulation to ensure a spawn configuration is escapable.
        For 1 player — original logic (full road).
        For 2 players — independent safety checks in left half (player with smaller x)
        and right half (player with larger x).
        Parameters
        ----------
        candidates : list of Obstacle
            Proposed obstacles to spawn.
        player_rects : list of pg.Rect
            Hitboxes of 1 or 2 players.
        Returns
        -------
        bool
            True if safe path(s) exist for all players in their halves, False otherwise.
        """
        sim_obstacles = self.obstacles + candidates

        def lane_from_rect(rect):
            lane = int((rect.centerx - C.LANE_OFFSET) / C.LANE_WIDTH)
            return max(0, min(C.LANES - 1, lane))

        if len(player_rects) == 1:
            lane = lane_from_rect(player_rects[0])
            return self.escape_exists(lane, 0, C.LANES - 1, sim_obstacles)

        # ===== TWO PLAYERS =====
        p_left, p_right = sorted(player_rects, key=lambda r: r.centerx)
        left_lane = lane_from_rect(p_left)
        right_lane = lane_from_rect(p_right)
        mid = C.LANES // 2

        trapped = self.detect_trapped_player(player_rects)

        if trapped:
            lane = lane_from_rect(trapped)
            if trapped is p_left:
                safe_lane = 0
                for c in candidates:
                    if c.lane == safe_lane:
                        continue
            else:
                safe_lane = C.LANES - 1
                for c in candidates:
                    if c.lane == safe_lane:
                        continue

            return self.escape_exists(lane, 0 if trapped is p_left else mid, mid-1 if trapped is p_left else C.LANES-1, sim_obstacles)

        left_safe = self.escape_exists(left_lane, 0, mid - 1, sim_obstacles)
        right_safe = self.escape_exists(right_lane, mid, C.LANES - 1, sim_obstacles)
        return left_safe and right_safe

    def spawn(self, max_enemies, player_rects, base_speed=None):
        """
        Attempt to generate a new wave of obstacles based on difficulty metrics.
        Supports 1 or 2 players via player_rects.
        Parameters
        ----------
        max_enemies : float
            Difficulty factor determining potential obstacle density.
        player_rects : list of pg.Rect
            Hitboxes of the player(s) — 1 or 2 elements.
        base_speed : float, optional
            The reference speed for scaling obstacle movement.
        """
        if base_speed is None:
            base_speed = 360

        trapped = None
        if len(player_rects) == 2:
            trapped = self.detect_trapped_player(player_rects)
            mid = C.LANES // 2
            if trapped is not None:
                safe_lane = 0 if trapped == sorted(player_rects, key=lambda r: r.centerx)[0] else C.LANES - 1

        attempts = 0
        while attempts < 25:
            obstacle_count = random.randint(1, max(1, int(C.LANES * max_enemies)))
            lanes = random.sample(range(C.LANES), obstacle_count)

            if trapped is not None and safe_lane in lanes:
                lanes.remove(safe_lane)

            candidates = []
            for lane in lanes:
                lane_type = self.get_lane_type(lane)
                mult_min, mult_max = self.speed_groups[lane_type]
                speed = base_speed * random.uniform(mult_min, mult_max)
                if self.lane_speeds[lane]:
                    speed = min(speed, min(self.lane_speeds[lane]))
                obstacle_type = random.choices(["CAR", "TRUCK"], [0.75, 0.25], k=1)[0]
                image = random.choices(self.images[obstacle_type], k=1)[0]
                if lane_type == TrafficType.OPPOSITE:
                    image = pg.transform.flip(image, False, True)
                obstacle = Obstacle(image, lane, -C.HEIGHT / 2, speed, direction=lane_type)
                candidates.append(obstacle)

            immediate_safe = not any(
                c.lane == o.lane and abs(c.rect.y - o.rect.y) < C.CAR_HEIGHT * 1.5
                for c in candidates
                for o in self.obstacles
            )
            if not immediate_safe:
                attempts += 1
                continue

            if self.is_spawn_safe(candidates, player_rects):
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
            if check_rect_collision(player_rect, o.rect):
                return o
        return None

    def draw(self, screen, is_night):
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