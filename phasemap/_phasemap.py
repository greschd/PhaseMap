#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    25.08.2016 14:58:52 CEST
# File:    phasemap.py

import math
import numbers
import itertools
from collections import namedtuple

import numpy as np
from fsc.export import export

PhaseResult = namedtuple('PhaseResult', ['phase', 'guess'])

@export
class PhaseMap:
    """data container"""
    def __init__(self, mesh, limits):
        """
        mesh is a list of integers
        limits is a list of tuples
        """
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
        self._steps = [1] * self.dim
        self.limits = list(tuple(l) for l in limits)
        self._data = np.empty(mesh, dtype=object)

    @property
    def result(self):
        return self._data[[
            slice(None, None, s) for s in self._steps
        ]]

    @property
    def phase(self):
        def map_phase(res):
            try:
                return res.phase
            except AttributeError:
                return None
        return np.array([
            map_phase(v) for v in self.result.flatten()
        ]).reshape(self.result.shape)
    
    @result.setter
    def result(self, value):
        self._data[[
            slice(None, None, s) for s in self._steps
        ]] = value
        
    @property
    def mesh(self):
        """
        Returns the shape of the current result
        """
        return self.result.shape

    @mesh.setter
    def mesh(self, mesh):
        k_list = [self._get_k(m, n) for m, n in zip(mesh, self.mesh)]
        for i, k in enumerate(k_list):
            self.extend_mesh(i, k=k)

    def extend_all(self, k=1):
        """increases mesh in all dimensions"""
        for i in range(self.dim):
            self.extend_mesh(i, k=k)
                
    def extend_mesh(self, dim, k=1):
        """Extends the mesh in a given dimension (k-fold). For negative k, the mesh is reduced by increasing the step."""
        # increase step for negative k
        if k < 0:
            self._steps[dim] *= 2**-k
            if (self._data.shape[dim] - 1) % self._steps[dim] != 0:
                 raise ValueError('Cannot reduce dimension {} with mesh size {}.'.format(dim, self._data.shape[dim]))
        
        # reduce step for positive k while possible
        while k > 0 and self._steps[dim] > 1:
            assert self._steps[dim] % 2 == 0
            self._steps[dim] //= 2
            k -= 1
        # extend data
        if k > 0:
            new_data = np.empty(
                [
                    m if j != dim else 2**k * (m - 1) + 1
                    for j, m in enumerate(self._data.shape)
                ],
                dtype=object
            )
            new_data[[
                slice(None) if j != dim else slice(None, None, 2**k)
                for j in range(self.dim)
            ]] = self._data
            self._data = new_data
            
    @staticmethod
    def _get_k(m, n):
        k = math.log2((m - 1) / (n - 1))
        # round to integer
        res = math.floor(k + 0.5)
        if not np.isclose(res, k):
            raise ValueError('New mesh size {} is inconsistent with the given size {}.'.format(m, n))
        return res
                
    def indices(self):
        """Returns an iterator over the indices in the mesh."""
        return itertools.product(*[range(s) for s in self.mesh])

    def items(self):
        """returns iterator over (index, position, value) of all elements"""
        for idx in self.indices():
            yield idx, self.index_to_position(idx), self.result[idx]
        
    def index_to_position(self, idx):
        """Returns the position on the phase map corresponding to a given index."""
        pos_param = (i / (m - 1) for i, m in zip(idx, self.mesh))
        return [
            l[0] * (1 - x) + l[1] * x 
            for x, l in zip(pos_param, self.limits)
        ]
        
    def get_neighbours(self, idx):
        directions = itertools.product(range(-1, 2), repeat=self.dim)
        res = (tuple(np.array(d) + np.array(idx)) for d in directions)
        return (r for r in res if self._in_limits(r))
        
    def get_neighbour_results(self, idx):
        res = (self.result[tuple(i)] for i in self.get_neighbours(idx))
        return {r.phase for r in res if r is not None}
        
    def check_neighbour_results(self, idx):
        res = self.get_neighbour_results(idx)
        if len(res) == 1:
            return res.pop(), True
        else:
            return None, False
    
    def _in_limits(self, idx):
        return all(0 <= i < m for i, m in zip(idx, self.mesh))
        
    def update(self, idx, val):
        for i, v in zip(idx, val):
            self.result[i] = v
