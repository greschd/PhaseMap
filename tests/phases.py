def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0


def line(x, y):
    return 1 if x > 0.5 or y < 0.2 else 0


def phase1(coord):
    x, y, *_ = coord
    return line(x, y) + circle(x, y)


def phase2(coord):
    x, y, *_ = coord
    if x >= 0 and x < 0.3:
        if y > 0.4 and y < 0.6:
            return 1

    if x > 0.4 and x < 0.6:
        if y >= 0 and y < 0.6:
            return 1
    if x > 0.4 and x < 0.6:
        if y >= 0.6:
            return 2

    if x >= 0 and x < 0.1:
        if y >= 0 and y < 0.1:
            return 1

    if (x - 0.5)**2 + (y - 0.5)**2 < 0.1:
        return 3

    return 0
