"""
Collision detection utilities for rectangular game objects.

This module contains specialized functions to handle physical interactions
and overlap detection between players and obstacles using Axis-Aligned
Bounding Box (AABB) logic.
"""


def check_rect_collision(a, b):
    """
    Check for an intersection between two rectangular bounding boxes.

    Uses the AABB (Axis-Aligned Bounding Box) collision detection
    algorithm to determine if two rectangles overlap in 2D space.

    Parameters
    ----------
    a : pygame.Rect
        The first rectangular area to check.
    b : pygame.Rect
        The second rectangular area to check.

    Returns
    -------
    bool
        True if the rectangles overlap, False otherwise.

    Notes
    -----
    Collision is detected if all of the following conditions are met:
    - The right edge of 'a' is further right than the left edge of 'b'.
    - The left edge of 'a' is further left than the right edge of 'b'.
    - The bottom edge of 'a' is further down than the top edge of 'b'.
    - The top edge of 'a' is further up than the bottom edge of 'b'.
    """
    return (
        a.right > b.left and a.left < b.right and a.bottom > b.top and a.top < b.bottom
    )
