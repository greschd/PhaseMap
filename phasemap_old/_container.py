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
        self.limits = list(tuple(l) for l in limits)
        self._steps = [1] * self.dim
        self._neighbour_directions = [
            l for l in list(itertools.product([-1, 0, 1], repeat=self.dim))
            if l != tuple([0] * self.dim)
        ]

        if init_map is None:
            self._data = dict()
            # the step in going from indices (external repr.) to  keys (internal repr.) 
            # the mesh size of the internal representation
            self._mesh = list(mesh)
        else:
            # consistency check
            if self.limits != init_map.limits:
                raise ValueError("limits '{}' of init_map do not match the current limits '{}'".format(init_map.limits, limits))
            
            self._mesh = init_map._mesh
            self._data = init_map._data
            # convert size -- this takes care of getting the right steps
            self.mesh = list(mesh)
            
            
        
    @property
    def mesh(self):
        """
        Returns the shape (number of grid points in each direction) of the current result.
        """
        return tuple((m - 1) // s + 1 for m, s in zip(self._mesh, self._steps))
        

    @mesh.setter
    def mesh(self, mesh):
        k_list = [self._get_k(m, n) for m, n in zip(mesh, self.mesh)]
        for i, k in enumerate(k_list):
            self.extend_mesh(i, k=k)

    def extend_all(self, k=1):
        """increases mesh in all dimensions"""
        for i in range(self.dim):
            self.extend_mesh(dim=i, k=k)
                
    def extend_mesh(self, dim, k=1):
        """Extends the mesh in a given dimension (k-fold). For negative k, the mesh is reduced by increasing the step."""
        # increase step for negative k
        if k < 0:
            self._steps[dim] *= 2**-k
            if (self._mesh[dim] - 1) % self._steps[dim] != 0:
                 raise ValueError('Cannot reduce dimension {} with mesh size {}.'.format(dim, self._data.shape[dim]))
        
        # reduce step for positive k while possible
        while k > 0 and self._steps[dim] > 1:
            assert self._steps[dim] % 2 == 0
            self._steps[dim] //= 2
            k -= 1
        # extend data
        if k > 0:
            self._data = {
                tuple(kval * 2 if i == dim else kval for i, kval in enumerate(k)): v 
                for k, v in self._data.items()
            }
            self._mesh = [(m * 2 - 1) if i == dim else m for i, m in enumerate(self._mesh)] 
                
    def indices(self):
        """Returns a set containing the indices of the evaluated grid points"""
        keys_internal = self._data.keys()
        return {
            tuple(kval // s for kval, s in zip(k, self._steps)) 
            for k in keys_internal 
            if all(kval % s == 0 for kval, s in zip(k, self._steps))
        }
        
    def items(self):
        return self._data.items()
        
    def _to_key(self, idx):
        """Converts the index from external to internal representation."""
        return tuple(i * s for i, s in zip(external_idx, self._step))
        
    def _to_idx(self, key):
        if all(k % s == 0 for k, s in zip(key, self._steps)):
            return tuple(k // s for k, s in zip(key, self._steps))
        else:
            return None
        
    def __getitem__(self, idx):
        """Set an element of the phase map."""
        return self._data[self._to_key(idx)]
        
    def __setitem__(self, idx, val):
        """Get an element of the phase map."""
        self._data[self._to_key(idx)] = val

    def index_to_position(self, idx):
        """Returns the position on the phase map corresponding to a given index."""
        pos_param = (i / (m - 1) for i, m in zip(idx, self.mesh))
        return [
            l[0] * (1 - x) + l[1] * x 
            for x, l in zip(pos_param, self.limits)
        ]
        
    def get_neighbours(self, idx):
        res = (
            tuple([d + i for d, i in zip(direction, idx)]) 
            for direction in self._neighbour_directions
        )
        return (r for r in res if self._in_limits(r))
        
    def _get_neighbour_results(self, idx):
        res = set(self._data.get(k, None) for k in self.get_neighbours(idx)) - {None}
        return res
      
    def check_neighbour_results(self, idx):
        res = self._get_neighbour_results(idx)
        assert len(res) != 0
        if len(res) == 1:
            return True
        else:
            return False
    
    def _in_limits(self, idx):
        """Checks whether a given (external) index is within the bounds of the data."""
        return all(0 <= i < m for i, m in zip(idx, self.mesh))
        
    def update(self, idx, val):
        for i, v in zip(idx, val):
            self._data[i] = v
            
    @staticmethod
    def _get_k(m, n):
        k = math.log2((m - 1) / (n - 1))
        # round to integer
        res = math.floor(k + 0.5)
        if not np.isclose(res, k):
            raise ValueError('New mesh size {} is inconsistent with the given size {}.'.format(m, n))
        return res
            
    #~ def to_array(self, dtype=object):
        #~ res = np.empty(self.mesh, dtype=dtype)
        #~ for k, v in self.keys():
            #~ res[k] = v
        #~ return res
    
