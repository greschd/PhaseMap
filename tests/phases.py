def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0


def line(x, y):
    return 1 if x > 0.5 or y < 0.2 else 0


def phase1(coord):
    x, y, *_ = coord
    return line(x, y) + circle(x, y)


def phase2(coord):
    x, y, *_ = coord
    if 0 <= x < 0.3:
        if 0.4 < y < 0.6:
            return 1

    if 0.4 < x < 0.6:
        if 0 <= y < 0.6:
            return 1
    if 0.4 < x < 0.6:
        if y >= 0.6:
            return 2

    if 0 <= x < 0.1:
        if 0 <= y < 0.1:
            return 1

    if (x - 0.5)**2 + (y - 0.5)**2 < 0.1:
        return 3

    return 0


def phase3(coord):
    x, y = coord
    if 0 <= x < 0.398:
        if 0.4 < y < 0.6:
            return 1

    if 0.4 < x < 0.6:
        if 0 <= y < 0.6:
            return 1
    if 0.4 < x < 0.6:
        if y >= 0.6:
            return -2

    if 0 <= x < 0.1:
        if 0 <= y < 0.1:
            return 1

    if (x - 0.5)**2 + (y - 0.5)**2 < 0.1:
        return 3

    return 0
