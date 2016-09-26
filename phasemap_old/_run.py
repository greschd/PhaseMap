#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    17.09.2016 13:55:07 CEST
# File:    _run.py

import numbers
import itertools

import numpy as np
from fsc.export import export

from ._container import PhaseMap
from ._logging_setup import logger

@export
def get_phase_map(fct, limits, init_mesh=5, num_steps=5, init_result=None):
    """
    init_mesh as int -> same in all dimensions. Otherwise as list of int.
    """
    # setting up the PhaseMap object
    if isinstance(init_mesh, numbers.Integral):
        init_mesh = [init_mesh] * len(limits)
    
    result_map = PhaseMap(mesh=init_mesh, limits=limits, init_map=init_result)
    
    # initial calculation
    # calculate for every grid point
    initial_idx = list(itertools.product(*[range(n) for n in init_mesh]))
    result_map.update(
        initial_idx, 
        fct([result_map.index_to_position(i) for i in initial_idx])
    )
    
    for step in range(num_steps):
        logger.info('Starting mapping step {}'.format(step))
        result_map.extend_all()
        # collect all neighbours (not yet calculated)
        neighbours = set()
        for i in result_map.indices():
            neighbours.update(result_map.get_neighbours(i))
        
        while neighbours:
            # check for those where not all neighbours have the same value
            to_calculate = [
                n for n in neighbours 
                if not result_map.check_neighbour_results(n)
            ]
            logger.info('found {} points to calculate'.format(len(to_calculate)))
            result_map.update(
                to_calculate, 
                fct([result_map.index_to_position(i) for i in to_calculate])
            )
            # collect neighbours of newly calculated values
            neighbours = set()
            for i in to_calculate:
                neighbours.update(result_map.get_neighbours(i))
            neighbours = neighbours - result_map.indices()

    return result_map

def _split_idx_pos(iterable):
    l = list(iterable)
    idx = [i for i, *_ in l]
    pos = [p for _, p, *_ in l]
    return idx, pos
