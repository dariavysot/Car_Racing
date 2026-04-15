import pytest
from pygame import Rect

from gameplay.collision import check_rect_collision


@pytest.mark.physics
class TestCollisionLogic:
    """Tests for the mathematical AABB collision detection logic."""

    def test_collision_full_overlap(self):
        """Full overlap: rectangles occupy the exact same space."""
        rect_a = Rect(100, 100, 50, 50)
        rect_b = Rect(100, 100, 50, 50)
        assert check_rect_collision(rect_a, rect_b) is True

    def test_collision_partial_overlap(self):
        """Partial overlap: rectangles intersect but are not identical."""
        rect_a = Rect(100, 100, 50, 50)
        rect_b = Rect(125, 125, 50, 50)
        assert check_rect_collision(rect_a, rect_b) is True

    def test_collision_edge_touch(self):
        """Edge touch: boundaries meet but do not overlap (should be False)."""
        rect_a = Rect(100, 100, 50, 50)
        rect_b = Rect(150, 100, 50, 50)
        assert check_rect_collision(rect_a, rect_b) is False

    @pytest.mark.smoke
    def test_no_collision(self):
        """No contact: objects are positioned far apart."""
        rect_a = Rect(0, 0, 10, 10)
        rect_b = Rect(100, 100, 10, 10)
        assert check_rect_collision(rect_a, rect_b) is False
