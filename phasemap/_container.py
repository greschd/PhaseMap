import itertools
from fractions import Fraction

import numpy as np
from fsc.export import export


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


class Point:
    """
    The squares are stored by their index in the PhaseMap.squares list.
    """

    def __init__(self, phase):
        self.phase = phase
        self.squares = set()


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
        self.points = set()

    def contains_point(self, point):
        return np.all(self.corner <= point
                      ) and np.all(point <= self.corner + self.size)


@export
class PhaseMap:
    """
    Data container for the phase diagram.

    :param mesh: Number of grid points in each spatial dimension.
    :type mesh: List[int]

    :param limits: Range of the phase diagram in each dimension.
    :type limits: List[List[float]]

    :param all_corners: Flag which determines if all corners of each square are calculated, or only those along one diagonal.
    :type all_corners: bool

    :param init_map: Initial result.
    :type init_map: PhaseMap
    """

    def __init__(self, mesh, limits, all_corners=False, init_map=None):
        # consistency checks
        if len(mesh) != len(limits):
            raise ValueError(
                'Inconsistent dimensions for mesh ({}) and limits ({})'.format(
                    mesh, limits
                )
            )
        if min(mesh) <= 1:
            raise ValueError('Mesh size must be at least 2 in each direction.')
        for l in limits:
            if len(l) != 2:
                raise ValueError('Limit {} does not have length 2.'.format(l))

        self.dim = len(mesh)
        self.mesh = list(mesh)
        self.step_sizes = [Fraction(1, m - 1) for m in self.mesh]
        self.limits = list(tuple(l) for l in limits)
        if init_map is None:
            self.points = dict()
        else:
            self.points = init_map.points
            # remove squares
            for v in self.points.values():
                v.squares = set()
        self.squares = list()
        self.all_corners = all_corners
        self._to_split = []
        self._to_calculate = []
        self._split_next = []

    def get_initial_points_frac(self):
        return set([
            Coordinate([i * s for i, s in zip(idx, self.step_sizes)])
            for idx in itertools.product(*[range(m) for m in self.mesh])
        ]) - self.points.keys()

    def create_initial_squares(self):
        for i, corner in enumerate([
            Coordinate([i * s for i, s in zip(idx, self.step_sizes)])
            for idx in itertools.product(*[range(m - 1) for m in self.mesh])
        ]):
            self.squares.append(Square(corner=corner, size=self.step_sizes))
            for pt in itertools.product(
                *[(c, c + s) for c, s in zip(corner, self.step_sizes)]
            ):
                self.add_point_to_square(point_frac=pt, square_idx=i)

    def fraction_to_position(self, frac):
        """Returns the position on the phase map corresponding to a given fraction."""
        return [l[0] * (1 - x) + l[1] * x for x, l in zip(frac, self.limits)]

    def step_done(self):
        """Returns whether the current step is completely done."""
        return not (self._to_calculate or self._to_split)

    def add_point_to_square(self, *, point_frac, square_idx):
        """
        Add a point to a given square. This adds the square to the point's list of squares and vice versa. If necessary the square is added to the relevant list of squares (to calculate now, to calculate in the next step).
        """
        if self.squares[square_idx].contains_point(point_frac):
            point = self.points[point_frac]
            square = self.squares[square_idx]
            square.points.add(point_frac)
            point.squares.add(square_idx)
            # adding the first point determines the phase
            if square.phase is None and len(square.points) == 1:
                square.phase = point.phase
            # check whether the phase is inconsistent
            elif (square.phase is not None) and (square.phase != point.phase):
                square.phase = None
                # larger squares can be split in the current iteration
                if np.any(square.size > self.step_sizes):
                    assert np.all(square.size > self.step_sizes)
                    assert square_idx not in self._to_calculate
                    self._to_calculate.append(square_idx)
                else:
                    assert square_idx not in self._split_next
                    self._split_next.append(square_idx)

    def decrease_step(self):
        self.step_sizes = [s / 2 for s in self.step_sizes]
        assert not self._to_calculate
        self._to_calculate = self._split_next
        self._split_next = []

    def _get_new_pts(self, square_idx):
        """Returns the points to calculate for splitting a given square."""
        pts_new = set()
        square = self.squares[square_idx]
        assert np.all(square.size > self.step_sizes)
        # corner points
        if self.all_corners:
            pts_new.update(
                Coordinate(x) for x in itertools.product(
                    *[(c, c + s / 2, c + s)
                      for c, s in zip(square.corner, square.size)]
                )
            )
        else:
            pts_new.update(
                Coordinate(x) for x in itertools.product(
                    *[(c, c + s) for c, s in zip(square.corner, square.size)]
                )
            )
            # middle point
            pts_new.add(
                Coordinate([
                    c + s / 2 for c, s in zip(square.corner, square.size)
                ])
            )
        return pts_new

    def pts_to_calculate(self):
        """
        Returns a set of points which need to be calculated for the squares that are marked for calculation. When done, it marks these squares for splitting.
        """
        pts_all = set()
        for square_idx in self._to_calculate:
            pts_all.update(self._get_new_pts(square_idx))
        self._to_split = self._to_calculate
        self._to_calculate = []
        return list(pts_all - self.points.keys())

    def update(self, pts_frac, values):
        """
        Sets the value for the given points.

        :param pts: A list of tuples, giving the fractional coordinate of the points.

        :param values: The values corresponding to each point.
        :type values: list
        """
        for p, v in zip(pts_frac, values):
            self.points[p] = Point(phase=v)

    def split_all(self):
        """Splits all squares that are currently marked for splitting."""
        for square_idx in self._to_split:
            self.split_square(square_idx)
        self._to_split = []
        assert len(self._to_split) == 0

    def get_neighbour_pts(self, point_frac, step):
        # if all corners are calculated, the neighbours with the relevant squares can be further away
        if self.all_corners:
            for dist in itertools.product(range(-3, 4), repeat=self.dim):
                yield Coordinate([
                    p + d * (s / 2) for p, d, s in zip(point_frac, dist, step)
                ])
        else:
            for i, s in enumerate(step):
                for direction in [-1, 1]:
                    yield Coordinate([
                        p + s * direction if i == j else p
                        for j, p in enumerate(point_frac)
                    ])

    def split_square(self, square_idx):
        old_square = self.squares[square_idx]

        # get points which have not been added to the square yet
        new_pts = self._get_new_pts(square_idx)
        old_pts = old_square.points
        for p in old_pts:
            self.points[p].squares.remove(square_idx)
        # get neighbouring squares for new points
        for p in new_pts - old_pts:
            square_candidates = set()
            for n in self.get_neighbour_pts(p, step=old_square.size):
                pt = self.points.get(n, None)
                if pt is None:
                    continue
                square_candidates.update(pt.squares)
            for s in square_candidates:
                self.add_point_to_square(square_idx=s, point_frac=p)
        all_pts = new_pts | old_pts

        # create new squares
        new_size = old_square.size / 2
        new_squares = [
            Square(corner=corner, size=new_size)
            for corner in itertools.product(
                *[(c, c + s) for c, s in zip(old_square.corner, new_size)]
            )
        ]
        # replace square in container
        num_squares_before = len(self.squares)
        self.squares[square_idx] = new_squares[0]
        self.squares.extend(new_squares[1:])
        new_square_indices = [square_idx] + list(
            range(num_squares_before, len(self.squares))
        )

        # find new square(s) for each point
        for p in all_pts:
            for n in new_square_indices:
                self.add_point_to_square(point_frac=p, square_idx=n)
