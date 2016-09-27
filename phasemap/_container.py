#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.09.2016 11:31:24 CEST
# File:    _container.py

import math
import copy
import numbers
import itertools

import numpy as np
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
        
class StepDict:
    def __init__(self, step, data=None):
        self.step = list(step)
        self.data = data if data is not None else dict()
        
    def _idx_to_key(self, idx):
        return tuple(i * s for i, s in zip(idx, self.step))
        
    def __getitem__(self, idx):
        return self.data[self._idx_to_key(idx)]
        
    def __setitem__(self, idx, value):
        self.data[self._idx_to_key(idx)] = value
        
    def get(self, idx, default=None):
        return self.data.get(self._idx_to_key(idx), default)
        
    def keys(self):
        res = set()
        for key in self.data.keys():
            if all(k % s == 0 for k, s in zip(key, self.step)):
                res.add(tuple(k // s for k, s in zip(key, self.step)))
        return res
        
    def values(self):
        res = []
        for key, val in self.data.items():
            if all(k % s == 0 for k, s in zip(key, self.step)):
                res.append(val)
        return res
        
    def items(self):
        res = []
        for key, val in self.data.items():
            if all(k % s == 0 for k, s in zip(key, self.step)):
                res.append((tuple(k // s for k, s in zip(key, self.step)), val))
        return res
        
    def extend(self, k_list=1):
        if isinstance(k_list, numbers.Integral):
            k_list = [k_list] * len(self.step)
        for i in range(len(self.step)):
            if k_list[i] < 0:
                self.step[i] *= 2**-k_list[i]
                k_list[i] = 0
            while self.step[i] > 1 and k_list[i] > 0:
                assert self.step[i] % 2 == 0
                k_list[i] -=1
                self.step[i] //= 2
        self.data = {
            tuple(i * 2**k for i, k in zip(idx, k_list)): val
            for idx, val in self.data.items()
        }

@export
class PhaseMap:
    def __init__(self, mesh, limits, all_corners=False, init_map=None):
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
        if init_map is None:
            self.points = StepDict(step=[1] * self.dim)
        else:
            self.points = init_map.points
            # remove squares
            for v in self.points.values():
                v.squares = set()
            # set the correct step or extend the points
            k_list = [self._get_k(m, n) for m, n in zip(self.mesh, init_map.mesh)]
            self.points.extend(k_list)
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
        
    def step_done(self):
        """Returns whether the current step is completely done."""
        return not (self._to_calculate or self._to_split)

    def add_point(self, *, point_idx, square_idx):
        """
        Add a point to a given square. This adds the square to the point's list of squares and vice versa. If necessary the square is added to the relevant list of squares (to calculate now, to calculate in the next step).
        """
        if self.pt_in_square(point_idx=point_idx, square_idx=square_idx):
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
        """Doubles the size of the system, adjusting the points and squares accordingly."""
        self.mesh = [2 * m - 1 for m in self.mesh]
        self.points.extend()
        for s in self.squares:
            s.size *= 2
            s.points = {tuple(2 * p for p in pt) for pt in s.points}
            s.corner = tuple(2 * c for c in s.corner)
        # split_next are now to calculate (size > 1)
        self._to_calculate = self._split_next
        self._split_next = []

    def _get_new_pts(self, square_idx):
        """Returns the points to calculate for splitting a given square."""
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
        """
        Returns a set of points which need to be calculated for the squares that are marked for calculation. When done, it marks these squares for splitting.
        """
        pts_all = set()
        for square_idx in self._to_calculate:
            pts_all.update(self._get_new_pts(square_idx))
        self._to_split = self._to_calculate
        self._to_calculate = []
        return list(pts_all - self.points.keys())

    def update(self, pts, values):
        """
        Sets the value for the given points.
        
        :param pts: A list of tuples, giving the index of the points.
        
        :param values: The values corresponding to each point.
        :type values: list
        """
        for p, v in zip(pts, values):
            self.points[p] = Point(phase=v)

    def split_all(self):
        """Splits all squares that are currently marked for splitting."""
        for square_idx in self._to_split:
            self.split_square(square_idx)
        self._to_split = []
        assert len(self._to_split) == 0

    def pt_in_square(self, *, point_idx, square_idx):
        """Checks whether a given point is within a square."""
        square = self.squares[square_idx]
        return all(
            p >= c and p <= c + square.size
            for p, c in zip(point_idx, square.corner)
        )

    def get_neighbour_pts(self, point_idx, step):
        # if all corners are calculated, the neighbours with the relevant squares can be further away
        if self.all_corners:
            assert step % 2 == 0
            for dist in itertools.product(range(-3, 4), repeat=self.dim):
                yield tuple(p + d * (step // 2) for p, d in zip(point_idx, dist))
        else:
            for i in range(self.dim):
                for s in [-step, step]:
                    yield tuple(p + s if i == j else p for j, p in enumerate(point_idx))

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

    @staticmethod     
    def _get_k(m, n):         
        k = math.log2((m - 1) / (n - 1))         
        # round to integer         
        res = math.floor(k + 0.5)         
        if not np.isclose(res, k):             
            raise ValueError('New mesh size {} is inconsistent with the given size {}.'.format(m, n))         
        return res   
