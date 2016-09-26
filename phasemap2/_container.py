#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.09.2016 11:31:24 CEST
# File:    _container.py

import copy
import math
import itertools
import contextlib
from collections import namedtuple

import numpy as np
from fsc.export import export

class Point:
    def __init__(self, phase):
        self.phase=phase
        self.squares = set()

class Square:
    def __init__(self, position, size=1):
        self.position = tuple(position)
        self.phase = None
        self.size = size
        self.points = set()

class PhaseMap:
    def __init__(self, mesh, limits):
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
        self._to_split = set()
        self._to_calculate = set()
        self._split_next = set()
        
    def create_initial_squares(self):
        for i, position in enumerate(itertools.product(*[range(n - 1) for n in self.mesh])):
            self.squares.append(Square(position=position))
            for pt in itertools.product(*[(p, p + 1) for p in position]):
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
                    self._to_calculate.add(square_idx)
                # size 1 squares will be split in the next iteration
                else:
                    self._split_next.add(square_idx)
    
    def extend(self):
        """Double the indices"""
        self.mesh = [2 * m - 1 for m in self.mesh]
        self.points = {tuple(2 * p for p in pt): v for pt, v in self.points.items()}
        for s in self.squares:
            s.size *= 2
            s.points = {tuple(2 * p for p in pt) for pt in s.points}
            s.position = tuple(2 * p for p in s.position)
        # split_next are now to calculate (size > 1)
        self._to_calculate = self._to_calculate | self._split_next
        self._split_next = set()
            
    def _get_new_pts(self, square_idx):
        pts_new = set()
        square = self.squares[square_idx]
        assert square.size % 2 == 0
        # position points
        pts_new.update(itertools.product(*[
            (p, p + square.size) for p in square.position
        ]))
        # middle point
        pts_new.add(tuple(p + square.size // 2 for p in square.position))
        return pts_new
            
    def pts_to_calculate(self):
        pts_all = set()
        for square_idx in self._to_calculate:
            pts_all.update(self._get_new_pts(square_idx))
        self._to_split = copy.deepcopy(self._to_calculate)
        self._to_calcualte = set()
        return list(pts_all - self.points.keys())
        
    def update(self, pts, values):
        for p, v in zip(pts, values):
            self.points[p] = Point(phase=v)
    
    def split_all(self):
        for square_idx in list(self._to_split):
            self.split_square(square_idx)
        assert len(self._to_split) == 0
    
    def pt_in_square(self, *, pt_idx, square_idx):
        square = self.squares[square_idx]
        return all(
            p_i >= s_p and p_i <= s_p + square.size 
            for p_i, s_p in zip(pt_idx, square.position)
        )
        
    def get_neighbour_pts(self, pt_idx, step):
        for i in range(self.dim):
            for s in [-step, step]:
                yield tuple(p + s if i == j else p for j, p in enumerate(pt_idx))
    
    def split_square(self, square_idx):
        # remove square from to_split and to_calculate
        self._to_split.remove(square_idx)
        self._to_calculate.remove(square_idx)

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
                #~ if self.pt_in_square(square_idx=s, pt_idx=p):
                self.add_point(square_idx=s, point_idx=p)
        all_pts = new_pts | old_pts
        
        # create new squares
        assert old_square.size % 2 == 0
        new_size = old_square.size // 2
        new_squares = [
            Square(position=position, size=new_size)
            for position in itertools.product(*[(e, e + new_size) for e in old_square.position])
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

