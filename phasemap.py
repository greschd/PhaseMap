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
        if len(mesh) != len(limits):
            raise ValueError('inconsistent dimensions for mesh ({}) and limits ({})'.format(mesh, limits))
        self.limits = limits
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
        pass
    
@export
def get_phase_map(fct, limits, init_mesh=5, num_steps=15):
    """
    init_mesh as int -> same in all dimensions. Otherwise as list of int.
    """
