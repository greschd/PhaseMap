from fractions import Fraction

import numpy as np


class Coordinate(np.ndarray):
    def __new__(cls, coord):
        coord_list = [Fraction(x) for x in coord]
        self = super().__new__(cls, shape=(len(coord_list), ), dtype=object)
        self[:] = coord_list
        self.flags.writeable = False
        return self

    def __hash__(self):
        return hash(tuple(self))

    def __eq__(self, other):
        return super().__eq__(other).all()
