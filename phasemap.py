#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    25.08.2016 14:58:52 CEST
# File:    phasemap.py

from __future__ import division, print_function

import sys
import math
import numbers
import logging
import itertools
from collections import namedtuple

import numpy as np
from fsc.export import export

__version__ = '0.0.0a1'

logger = logging.getLogger('phasemap')
logger.setLevel(logging.INFO)
DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
#~ DEFAULT_HANDLER.setFormatter(logging.)
#~ logging.getLogger('z2pack').setLevel(logging.INFO)
logger.addHandler(DEFAULT_HANDLER)

PhaseResult = namedtuple('PhaseResult', ['phase', 'guess'])

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

@export
def get_phase_map(fct, limits, init_mesh=5, num_steps=15, init_result=None):
    """
    init_mesh as int -> same in all dimensions. Otherwise as list of int.
    """
    # setting up the PhaseMap object
    if isinstance(init_mesh, numbers.Integral):
        init_mesh = [init_mesh] * len(limits)
    
    if init_result is not None:
        result_map = init_result
        result_map.mesh = init_mesh
        if not np.isclose(np.array(limits), np.array(result.limits)).all():
            raise ValueError("'init_result' limits {} do not match limits {}".format(result.limits, limits))
    else:
        result_map = PhaseMap(mesh=init_mesh, limits=limits)
    
    # initial calculation
    # calculate for all guesses and new entries
    idx, pos = _split_idx_pos(
        (i, p) for i, p, v in result_map.items()
        if v is None or v.guess
    )
    result_map.update(
        idx, 
        [PhaseResult(v, guess=False) for v in fct(pos)]
    )
    
    for step in range(num_steps):
        logger.info('Starting mapping step {}'.format(step))
        result_map.extend_all()

        # check new -- which have all the same neighbours?
        idx = []
        pos = []
        for i, p, v in result_map.items():
            if v is not None:
                continue
            val, flag = result_map.check_neighbour_results(i)
            if flag:
                result_map.result[tuple(i)] = PhaseResult(val, guess=True)
            else:
                idx.append(i)
                pos.append(p)
        result_map.update(
            idx,
            [PhaseResult(v, guess=False) for v in fct(pos)]
        )
        
        # second round -- check guesses again
        to_check = set(i for i, p, v in result_map.items() if v.guess)
        while to_check:
            to_measure = []
            old_result = []
            while to_check:
                idx = to_check.pop()
                val, same = result_map.check_neighbour_results(idx)
                if not same:
                    to_measure.append(i)
                    old_result.append(result_map.result[i])
            new_result = [
                PhaseResult(n, guess=False) for n in fct(to_measure)
            ]
            result_map.update(to_measure, new_result)
            for i, n, o in zip(to_measure, new_result, old_result):
                if n.phase != o.phase:
                    to_check.update({
                        idx for idx in result_map.get_neighbours(i)
                        if result_map.result[tuple(idx)].guess
                    })

    return result_map

def _update_result(res, idx, val):
    for i, v in zip(idx, val):
        res.result[i] = v

def _split_idx_pos(iterable):
    l = list(iterable)
    idx = [i for i, *_ in l]
    pos = [p for _, p, *_ in l]
    return idx, pos
