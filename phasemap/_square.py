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

    def __hash__(self):
        return hash((self.corner, self.size))

    def contains_point(self, point):
        return np.all(self.corner <= point) and np.all(point <= self.corner + self.size)

    def is_neighbour(self, other):
        assert np.all(self.corner != other.corner)
        return (
            np.all(self.corner + self.size >= other.corner) and
            np.all(other.corner + other.size >= self.corner)
        )

    def process_possible_neighbour(self, square):
        if self.is_neighbour(square):
            self.add_neighbour(square)
            square.add_neighbour(self)

    def add_neighbour(self, square):
        self.neighbours.add(square)

    def delete_from_neighbours(self):
        for n in self.neighbours:
            n.delete_neighbour(self)

    def delete_neighbour(self, square):
        self.neighbours.discard(square)
