#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    26.05.2016 16:22:14 CEST
# File:    phase_finder.py

from __future__ import division, print_function

import sys
import copy
import pickle
import itertools
from collections import ChainMap

import numpy as np
import scipy.linalg as la

from ptools.tolerantfloat import tolerantfloat, toleranttuple
from ptools.monitoring import Timer
#~ from ptools.spatial_data import cache_spatial_data

class PhaseFinder(object):
    def __init__(self, fct, limits, tol=1e-8):
        self.fct = fct
        self.limits = limits
        self.dim = len(limits)
        self.results_measured = {}
        self.results_virtual = {}
        self.results = ChainMap(self.results_measured, self.results_virtual)
        self.tol = tol
        self.FloatType = tolerantfloat('FloatType', tol)
        self.TupleType = toleranttuple('TupleType', tol)

    def run(self, init_mesh, num_steps=15, min_dist=None, follow_virtuals=False, neighbour_range=2):
        self.neighbour_range = neighbour_range
        self.mesh = np.array(init_mesh)
        self.steps = np.array([l[1] - l[0] for l in self.limits]) / (self.mesh - 1)
        #~ print(self.steps)
        
        grid = self._create_grid()
        self.results_measured.update({p: v for p, v in zip(grid, self.fct(grid))})
        
        for i in range(num_steps):
            print(i)
            self.mesh = (self.mesh - 1) * 2 + 1
            self.steps /= 2
            #~ print(self.steps)
            # STEP 1 -- check "old" neighbours and see if the new value should be measured or virtual
            to_measure = []
            new_virtual = {}
            pos = self._create_grid()
            for p in pos:
                if p not in self.results.keys():
                    #~ print(self.steps)
                    val, same = self._check_neighbour_results(p)
                    if same:
                        new_virtual[p] = val
                    else:
                        to_measure.append(p)
            # this is only for "niceness" of the output -- could be omitted
            to_measure = sorted(to_measure)
            self.results_measured.update({p: v for p, v in zip(to_measure, self.fct(to_measure))})
            self.results_virtual.update(new_virtual)
            
            #~ for p in pos:
                #~ assert p in self.results.keys()
    
            # STEP 2 -- now check whether some virtuals need to be updated
            to_check = set(self.results_virtual.keys())
            while to_check:
                to_measure = set()
                while to_check:
                    p = to_check.pop()
                    val, same = self._check_neighbour_results(p)
                    if not same or val != self.results_virtual[p]:
                        to_measure.add(p)
                to_measure = list(to_measure)
                self.results_measured.update({p: v for p, v in zip(to_measure, self.fct(to_measure))})
                
                # add neighbours of changed nodes to "to_check"
                for p in to_measure:
                    if self.results_measured[p] != self.results_virtual[p]:
                        to_check.update(self._get_neighbours(p))
                    # delete all measured values from virtual results
                    del self.results_virtual[p]
                # make sure the points to check are virtuals
                to_check = {p for p in to_check if p in self.results_virtual.keys()}

            # DEBUG: For performance analysis
            print('all:', len(self.results.keys()))
            print('measured:', len(self.results_measured.keys()))

    def _get_neighbours(self, pos):
        directions = itertools.product(range(-self.neighbour_range, self.neighbour_range + 1), repeat=self.dim)
        directions_nonzero = (d for d in directions if d != tuple([0] * self.dim))
        neighbours = (np.array(pos) + np.array(d) * self.steps for d in directions_nonzero)
        return [self.TupleType(n) for n in neighbours]

    def _get_neighbour_results(self, pos):
        res = []
        for n in self._get_neighbours(pos):
            try:
                res.append(self.results[n])
            except KeyError:
                pass
        return res
        
    def _check_neighbour_results(self, pos):
        neighbour_res = self._get_neighbour_results(pos)
        if len(neighbour_res) == 0:
            # TODO: this problem needs to be fixed on a more fundamental level.
            # The datastructure used has to maybe be changed.
            raise ValueError('No neighbours found for point {}. Make sure the tolerance is sufficiently large.'.format(pos))
        candidate = neighbour_res[0]
        if all([r == candidate for r in neighbour_res]):
            return candidate, True
        else:
            return None, False

    def _in_limits(self, p):
        """
        Checks if the point p is inside the limits.
        """
        for pval, limit in zip(p, self.limits):
            if pval < limit[0] or pval > limit[1]:
                return False
        else:
            return True

    def _create_grid(self):
        """
        Create a grid of a certain ``mesh`` in the given ``limits``.
        """
        linear_values = [np.linspace(l[0], l[1], m) for l, m in zip(self.limits, self.mesh)]
        return [self.TupleType(pval) for pval in itertools.product(*linear_values)]
