import pytest
from pygame import Rect
from gameplay.collision import check_rect_collision

@pytest.mark.physics
def test_collision_full_overlap():
    """Кейс: повне накладання прямокутників"""
    rect_a = Rect(100, 100, 50, 50)
    rect_b = Rect(100, 100, 50, 50)
    assert check_rect_collision(rect_a, rect_b) is True

@pytest.mark.physics
def test_collision_edge_touch():
    """Кейс: дотик краями"""
    rect_a = Rect(100, 100, 50, 50)
    rect_b = Rect(150, 100, 50, 50)
    assert check_rect_collision(rect_a, rect_b) is False

@pytest.mark.smoke
def test_no_collision():
    """Кейс: відсутність контакту"""
    rect_a = Rect(0, 0, 10, 10)
    rect_b = Rect(100, 100, 10, 10)
    assert check_rect_collision(rect_a, rect_b) is False