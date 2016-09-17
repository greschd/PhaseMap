#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    17.09.2016 13:55:07 CEST
# File:    _run.py

import numbers

from fsc.export import export

from ._containers import PhaseMap, PhaseResult
from ._logging_setup import logger

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
