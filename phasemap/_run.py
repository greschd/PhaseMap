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
def run(fct, limits, init_mesh=5, num_steps=5, all_corners=False, listable=True, init_result=None):
    """
    init_mesh as int -> same in all dimensions. Otherwise as list of int.
    """
    if not listable:
        fct_listable = lambda pts: [fct(p) for p in pts]
    else:
        fct_listable = fct
    # setting up the PhaseMap object
    if isinstance(init_mesh, numbers.Integral):
        init_mesh = [init_mesh] * len(limits)

    result_map = PhaseMap(
        mesh=init_mesh,
        limits=limits,
        all_corners=all_corners,
        init_map=init_result
    )

    # initial calculation
    # calculate for every grid point
    initial_idx = list(itertools.product(*[range(n) for n in init_mesh]))
    result_map.update(
        initial_idx,
        fct_listable([result_map.index_to_position(i) for i in initial_idx])
    )
    result_map.create_initial_squares()

    for step in range(num_steps):
        logger.info('starting evaluation step {}'.format(step))
        result_map.extend()
        while not result_map.step_done():
            to_calculate = result_map.pts_to_calculate()
            result_map.update(
                to_calculate,
                fct_listable([
                    result_map.index_to_position(i)
                    for i in to_calculate
                ])
            )
            result_map.split_all()

    return result_map
