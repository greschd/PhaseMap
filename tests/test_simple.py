#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.08.2016 04:11:07 CEST
# File:    test.py

import copy

import pytest
import numpy as np
import phasemap as pm

def circle(x, y, z=0):
    return 2 if x**2 + y**2 + z**2 < 1 else 0

def line(x, y, z=0):
    return 1 if x > 0.5 or y < 0.2 else 0

def phase1(val):
    return [line(*v) + circle(*v) for v in val]
    
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

@pytest.mark.parametrize('num_steps', range(0, 5))
@pytest.mark.parametrize('all_corners', [False, True])
@pytest.mark.parametrize('phase, listable, limits', [(phase1, True, [(-1, 1), (-1, 1)]), (phase2, False, [(0, 1), (0, 1)])])
def test_phase(compare_equal, num_steps, all_corners, phase, listable, limits):
    res = pm.run(phase, limits, num_steps=num_steps, init_mesh=3, all_corners=all_corners, listable=listable)
    compare_equal(sorted([(k, v.phase) for k, v in res.points.items()]))
    compare_equal(res, tag='with_encoding')

@pytest.mark.parametrize('num_steps', range(0, 3))
@pytest.mark.parametrize('all_corners', [False, True])
@pytest.mark.parametrize('phase, listable, limits', [(phase1, True, [(-1, 1), (-1, 1), (-1, 1)])])
def test_3d(compare_equal, num_steps, all_corners, phase, listable, limits):
    res = pm.run(phase, limits=limits, num_steps=num_steps, init_mesh=3, all_corners=all_corners, listable=listable)
    compare_equal(sorted([(k, v.phase) for k, v in res.points.items()]))
    compare_equal(res, tag='with_encoding')

@pytest.mark.parametrize('num_steps_1', range(3))
@pytest.mark.parametrize('num_steps_2', range(3))
def test_restart(results_equal, num_steps_1, num_steps_2):
    num_steps_total = num_steps_1 + num_steps_2
    res = pm.run(phase1, [(-1, 1), (-1, 1)], num_steps=num_steps_total, init_mesh=2)

    res2 = pm.run(phase1, [(-1, 1), (-1, 1)], num_steps=num_steps_1, init_mesh=2)
    res2 = pm.run(phase1, [(-1, 1), (-1, 1)], num_steps=num_steps_total, init_result=res2, init_mesh=2)
    assert sorted([(k, v.phase) for k, v in res.points.items()]) == sorted([(k, v.phase) for k, v in res2.points.items()])
    results_equal(res, res2)
