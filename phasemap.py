#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    25.08.2016 14:58:52 CEST
# File:    phasemap.py

from __future__ import division, print_function

import math
import itertools
from collections import namedtuple

import numpy as np
from fsc.export import export

__version__ = '0.0.0a1'

PhaseResult = namedtuple('PhaseResult', ['phase', 'virtual'])

@export
class PhaseMap(object):
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
        self._step = [1] * self.dim
        self.limits = list(tuple(l) for l in limits)
        self._data = np.empty(mesh, dtype=object)

    @property
    def result(self):
        return self._data[[
            slice(None, None, s) for s in self._step
        ]]
        
    @result.setter
    def result(self, value):
        self._data[[
            slice(None, None, s) for s in self._step
        ]] = value
        
    @property
    def mesh(self):
        """
        A way of getting self.result.shape without the matrix copying
        """
        return [
            ((m - 1) // s) + 1 
            for m, s in zip(self._data.shape, self._step)
        ]

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
            self._step[dim] *= 2**-k
            if (self._data.shape[dim] - 1) % self._step[dim] != 0:
                 raise ValueError('Cannot reduce dimension {} with mesh size {}.'.format(dim, self._data.shape[dim]))
        
        # reduce step for positive k while possible
        while k > 0 and self._step[dim] > 1:
            assert self._step[dim] % 2 == 0
            self._step[dim] //= 2
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
        return itertools.product(*[range(s) for s in self._data.shape])

    def items(self):
        """returns iterator over (index, position, value) of all elements"""
        for idx in self.indices():
            yield idx, self.index_to_position(idx), self._data[idx]
        
    def virtuals(self):
        """returns iterator over virtual elements (index, position, value)."""
        for idx, pos, val in self.items():
            if isinstance(val, PhaseResult) and val.virtual:
                yield idx, pos, val
        
    def new(self):
        """returns iterator over new elements (index, position, value is None). May assume that they are at the correct (odd) indices."""
        for idx, pos, val in self.items():
            if not isinstance(val, PhaseResult):
                yield idx, pos
        
    def index_to_position(self, idx):
        """Returns the position on the phase map corresponding to a given index."""
        pos_param = (i / (m - 1) for i, m in zip(idx, self.mesh))
        return [
            l[0] * (1 - x) + l[1] * x 
            for x, l in zip(pos_param, self.limits)
        ]
        
@export
def get_phase_map(fct, limits, init_mesh=5, num_steps=15):
    """
    init_mesh as int -> same in all dimensions. Otherwise as list of int.
    """
    pass
