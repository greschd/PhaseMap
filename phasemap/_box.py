import numpy as np

from ._coordinate import Coordinate


class Sentinel:
    __INSTANCES = dict()

    def __new__(cls, value):
        if value in cls.__INSTANCES:
            return cls.__INSTANCES[value]
        self = super().__new__(cls)
        self._value = value  # pylint: disable=protected-access
        cls.__INSTANCES[value] = self
        return self

    def __repr__(self):
        return 'Sentinel({!r})'.format(self._value)  # pylint: disable=no-member


PHASE_UNDEFINED = Sentinel('undefined phase')


class Box:
    """
    Class describing a "box" (or n-dimensional hyperrectangle).

    Attributes
    ----------
    corner: Coordinate
        The vertex with the lowest indices.
    size: Coordinate
        Size of the box.
    phase:
        The phase of the box, determined by the evaluated points it contains: If all points have the same phase, the box will have that phase. Otherwise, the phase of the box is undefined.
    """

    def __init__(self, *, corner, size):
        self.corner = Coordinate(corner)
        self.phase = None
        self.size = Coordinate(size)
        self._neighbours = set()
        self._points = dict()

    def __hash__(self):
        return hash((self.corner, self.size))

    def __eq__(self, other):
        return np.all(self.corner == other.corner
                      ) and np.all(self.size == other.size)

    def __repr__(self):
        return 'Box(corner={0.corner}, size={0.size}, phase={0.phase})'.format(
            self
        )

    def contains_coord(self, coord):
        # Faster than pure numpy operations because of the slow 'Fraction'.
        # In this way, the remaining operations are not performed if one
        # expression evaluates to False.
        return (
            all(c1 <= c2 for c1, c2 in zip(self.corner, coord)) and all(
                c2 <= c1 + s
                for c1, c2, s in zip(self.corner, coord, self.size)
            )
        )

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
        return all(
            c1 + s1 >= c2 and c2 + s2 >= c1 for c1, s1, c2, s2 in
            zip(self.corner, self.size, other.corner, other.size)
        )

    def process_possible_neighbour(self, box):
        if self.is_neighbour(box):
            self.process_certain_neighbour(box)

    def process_certain_neighbour(self, box):
        self._neighbours.add(box)
        box._neighbours.add(self)  # pylint: disable=protected-access

    def delete_from_neighbours(self):
        for n in self._neighbours:
            n.delete_neighbour(self)

    def delete_neighbour(self, box):
        self._neighbours.discard(box)
