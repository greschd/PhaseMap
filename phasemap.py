#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    25.08.2016 14:58:52 CEST
# File:    phasemap.py

import itertools
from collections import namedtuple

import numpy as np
from fsc.export import export

__version__ = '0.0.0a1'

PhaseResult = namedtuple('PhaseResult', ['phase', 'virtual'])

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

        self.limits = list(tuple(l) for l in limits)
        self.data = np.empty(mesh, dtype=object)
        
    def __getitem__(self, *args):
        return self.data.__getitem__(*args)
        
    def __setitem__(self, *args):
        self.data.__setitem__(*args)

    def extend(self):
        """increases mesh density"""
        new_data = np.empty([s * 2 - 1 for s in self.data.shape], dtype=object)
        for idx in self.indices():
            new_idx = tuple((i * 2) for i in idx)
            new_data[new_idx] = self.data[idx]
        self.data = new_data
        
    def indices(self):
        """Returns an iterator over the indices in the mesh."""
        return itertools.product(*[range(s) for s in self.data.shape])

    def items(self):
        """returns iterator over (index, position, value) of all elements"""
        for idx in self.indices():
            yield idx, self.index_to_position(idx), self.data[idx]
        
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
        pos_param = (i / (m - 1) for i, m in zip(idx, self.data.shape))
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
