#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.08.2016 04:11:07 CEST
# File:    test.py

import copy

import pytest
import numpy as np
import phasemap_old as pmo
import phasemap as pm

def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0

def line(x, y):
    return 1 if x > 0.5 or y < 0.2 else 0

def phase1(val):
    return [line(x, y) + circle(x, y) for x, y in val]
    
def phase2(pos):
    if pos[0] >= 0 and pos[0] < 0.3:
        if pos[1] > 0.4 and pos[1] < 0.6:
            return 1

    if pos[0] > 0.4 and pos[0] < 0.6:
        if pos[1] >= 0 and pos[1] < 0.6:
            return 1
    if pos[0] > 0.4 and pos[0] < 0.6:
        if pos[1] >= 0.6:
            return 2

    if pos[0] >= 0 and pos[0] < 0.1:
        if pos[1] >= 0 and pos[1] < 0.1:
            return 1

    return 0
    
def phase3(pos):
    x, y = pos
    if y > 0.8 and x < 0.6:
        return 1
    return 0


@pytest.mark.parametrize('num_steps', range(2, 5))
@pytest.mark.parametrize('all_corners', [False, True])
@pytest.mark.parametrize('phase,listable', [(phase1, True), (phase2, False)])
def test_phase(compare_equal, num_steps, all_corners, phase, listable):
    res = pm.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps=num_steps, init_mesh=3, all_corners=all_corners, listable=listable)
    compare_equal(sorted([(k, v.phase) for k, v in res.points.items()]))

#~ @pytest.mark.parametrize('num_steps', range(2, 5))
#~ @pytest.mark.parametrize('all_corners', [False, True])
#~ @pytest.mark.parametrize('phase,listable', [(phase1, True), (phase2, False)])
def test_same_square_idx(compare_equal):
    res = pm.get_phase_map(phase3, [(0, 1), (0, 1)], num_steps=2, init_mesh=2, listable=False)
    compare_equal(sorted([(k, v.phase) for k, v in res.points.items()]))
    # This can be used when the code is stable and io is done
    #~ compare_result(res)
