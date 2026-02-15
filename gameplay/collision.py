def check_rect_collision(a, b):
    return (
        a.right > b.left and
        a.left < b.right and
        a.bottom > b.top and
        a.top < b.bottom
    )