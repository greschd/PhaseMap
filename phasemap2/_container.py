#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.09.2016 11:31:24 CEST
# File:    _container.py

import math
import itertools

import numpy as np
from fsc.export import export

@export
class PhaseMap:
    """data container"""
    def __init__(self, mesh, limits, init_map=None):
        """
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
        self.mesh = list(mesh)
        self.limits = list(tuple(l) for l in limits)
        if init_map is None:
            self.data = dict()
            self._steps = [1] * self.dim
        else:
            # consistency checks
            raise NotImplementedError
            
        self._neighbour_directions = [
            l for l in list(itertools.product([-1, 0, 1], repeat=self.dim))
            if l != tuple([0] * self.dim)
        ]

    def extend_all(self, k=1):
        """increases mesh in all dimensions"""
        self.data = {tuple(kval * 2 for kval in k): v for k, v in self.data.items()}
        self.mesh = [(m - 1) * 2 + 1 for m in self.mesh]
                
    def keys(self):
        """Returns an iterator over the indices of the evaluated grid points"""
        return self.data.keys()
        
    def items(self):
        return self.data.items()

    def index_to_position(self, idx):
        """Returns the position on the phase map corresponding to a given index."""
        pos_param = (i / (m - 1) for i, m in zip(idx, self.mesh))
        return [
            l[0] * (1 - x) + l[1] * x 
            for x, l in zip(pos_param, self.limits)
        ]
        
    def get_neighbours(self, idx):
        res = (tuple([d + i for i in zip(dir, idx)]) for dir in self._neighbour_directions)
        return (r for r in res if self._in_limits(r))
        
    def _get_neighbour_results(self, idx):
        res = set(self.data.get(k, None) for k in self.get_neighbours(idx)) - {None}
        return res
      
    def check_neighbour_results(self, idx):
        res = self._get_neighbour_results(idx)
        assert len(res) != 0
        if len(res) == 1:
            return True
        else:
            return False
    
    def _in_limits(self, idx):
        return all(0 <= i < m for i, m in zip(idx, self.mesh))
        
    def update(self, idx, val):
        for i, v in zip(idx, val):
            self.data[i] = v
            
    def to_array(self, dtype=object):
        res = np.empty(self.mesh, dtype=dtype)
        for k, v in self.keys():
            res[k] = v
        return res
    
