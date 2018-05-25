class Square:
    """
    - corner is the vertex with the lowest indices
    - phase is None if there is no point in the square or there are points with different phases
    - the points are stored by their index (position)
    """

    def __init__(self, corner, size):
        self.corner = Coordinate(corner)
        self.phase = None
        self.size = Coordinate(size)
        self.neighbours = set()

    def contains_point(self, point):
        return np.all(self.corner <= point) and np.all(point <= self.corner + self.size)

    def is_neighbour(self, other):
        return (
            np.all(self.corner + self.size >= other.corner) and
            np.all(other.corner + other.size >= self.corner)
        )
