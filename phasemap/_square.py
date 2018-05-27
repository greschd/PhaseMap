import numpy as np

from ._coordinate import Coordinate

PHASE_UNDEFINED = object()


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
        self._points = dict()

    def __hash__(self):
        return hash((self.corner, self.size))

    def __eq__(self, other):
        return np.all(self.corner == other.corner
                      ) and np.all(self.size == other.size)

    def contains_coord(self, coord):
        return np.all(self.corner <= coord
                      ) and np.all(coord <= self.corner + self.size)

    def add_point(self, coord, phase):
        if self.contains_coord(coord):
            self._points[coord] = phase
            if self.phase is None:
                self.phase = phase
            elif self.phase == phase:
                return
            else:
                self.phase = PHASE_UNDEFINED

    def is_neighbour(self, other):
        assert not self.corner == other.corner
        return (
            np.all(self.corner + self.size >= other.corner)
            and np.all(other.corner + other.size >= self.corner)
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
