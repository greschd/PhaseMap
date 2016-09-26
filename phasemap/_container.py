#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.09.2016 11:31:24 CEST
# File:    _container.py

import itertools

from fsc.export import export

class Point:
    def __init__(self, phase):
        self.phase = phase
        self.squares = set()

class Square:
    def __init__(self, corner, size=1):
        self.corner = tuple(corner)
        self.phase = None
        self.size = size
        self.points = set()

@export
class PhaseMap:
    def __init__(self, mesh, limits, all_corners=False):
        # consistency checks
        if len(mesh) != len(limits):
            raise ValueError('Inconsistent dimensions for mesh ({}) and limits ({})'.format(mesh, limits))
        if min(mesh) <= 1:
            raise ValueError('Mesh size must be at least 2 in each direction.')
        for l in limits:
            if len(l) != 2:
                raise ValueError(
                    'Limit {} does not have length 2.'.format(l)
                )

        self.dim = len(mesh)
        self.mesh = list(mesh)
        self.limits = list(tuple(l) for l in limits)
        self.points = dict()
        self.squares = list()
        self.all_corners = all_corners
        self._to_split = []
        self._to_calculate = []
        self._split_next = []

    def create_initial_squares(self):
        for i, corner in enumerate(itertools.product(*[range(n - 1) for n in self.mesh])):
            self.squares.append(Square(corner=corner))
            for pt in itertools.product(*[(c, c + 1) for c in corner]):
                self.add_point(point_idx=pt, square_idx=i)

    def index_to_position(self, idx):
        """Returns the position on the phase map corresponding to a given index."""
        pos_param = (i / (m - 1) for i, m in zip(idx, self.mesh))
        return [
            l[0] * (1 - x) + l[1] * x
            for x, l in zip(pos_param, self.limits)
        ]

    def add_point(self, *, point_idx, square_idx):
        if self.pt_in_square(pt_idx=point_idx, square_idx=square_idx):
            point = self.points[point_idx]
            square = self.squares[square_idx]
            square.points.add(point_idx)
            point.squares.add(square_idx)
            # adding the first point determines the phase
            if square.phase is None and len(square.points) == 1:
                square.phase = point.phase
            # check whether the phase is inconsistent
            elif (square.phase is not None) and (square.phase != point.phase):
                square.phase = None
                # larger squares can be split in the current iteration
                if square.size > 1:
                    assert square_idx not in self._to_calculate
                    self._to_calculate.append(square_idx)
                # size 1 squares will be split in the next iteration
                else:
                    assert square_idx not in self._split_next
                    self._split_next.append(square_idx)

    def extend(self):
        """Double the indices"""
        self.mesh = [2 * m - 1 for m in self.mesh]
        self.points = {tuple(2 * p for p in pt): v for pt, v in self.points.items()}
        for s in self.squares:
            s.size *= 2
            s.points = {tuple(2 * p for p in pt) for pt in s.points}
            s.corner = tuple(2 * c for c in s.corner)
        # split_next are now to calculate (size > 1)
        self._to_calculate = self._split_next
        self._split_next = []

    def _get_new_pts(self, square_idx):
        pts_new = set()
        square = self.squares[square_idx]
        assert square.size % 2 == 0
        # corner points
        if self.all_corners:
            pts_new.update(itertools.product(*[
                (c, c + square.size // 2, c + square.size) for c in square.corner
            ]))
        else:
            pts_new.update(itertools.product(*[
                (c, c + square.size) for c in square.corner
            ]))
            # middle point
            pts_new.add(tuple(c + square.size // 2 for c in square.corner))
        return pts_new

    def pts_to_calculate(self):
        pts_all = set()
        for square_idx in self._to_calculate:
            pts_all.update(self._get_new_pts(square_idx))
        self._to_split = self._to_calculate
        self._to_calculate = []
        return list(pts_all - self.points.keys())

    def update(self, pts, values):
        for p, v in zip(pts, values):
            self.points[p] = Point(phase=v)

    def split_all(self):
        for square_idx in self._to_split:
            self.split_square(square_idx)
        self._to_split = []
        assert len(self._to_split) == 0

    def pt_in_square(self, *, pt_idx, square_idx):
        square = self.squares[square_idx]
        return all(
            p >= c and p <= c + square.size
            for p, c in zip(pt_idx, square.corner)
        )

    def get_neighbour_pts(self, pt_idx, step):
        # if all corners are calculated, the neighbours with the relevant squares can be further away
        if self.all_corners:
            assert step % 2 == 0
            for dist in itertools.product(range(-3, 4), repeat=self.dim):
                yield tuple(p + d * (step // 2) for p, d in zip(pt_idx, dist))
        else:
            for i in range(self.dim):
                for s in [-step, step]:
                    yield tuple(p + s if i == j else p for j, p in enumerate(pt_idx))

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
                self.add_point(square_idx=s, point_idx=p)
        all_pts = new_pts | old_pts

        # create new squares
        assert old_square.size % 2 == 0
        new_size = old_square.size // 2
        new_squares = [
            Square(corner=corner, size=new_size)
            for corner in itertools.product(*[(c, c + new_size) for c in old_square.corner])
        ]
        # replace square in container
        num_squares_before = len(self.squares)
        self.squares[square_idx] = new_squares[0]
        self.squares.extend(new_squares[1:])
        new_square_indices = [square_idx] + list(range(num_squares_before, len(self.squares)))

        # find new square(s) for each point
        for p in all_pts:
            for n in new_square_indices:
                self.add_point(point_idx=p, square_idx=n)

