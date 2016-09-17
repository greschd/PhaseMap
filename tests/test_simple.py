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

def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0

def line(x, y):
    return 1 if x > 0.5 or y < 0.2 else 0

def phase(val):
    return [line(x, y) + circle(x, y) for x, y in val]

@pytest.mark.parametrize('num_steps', range(2, 5))
def test_phase(compare_result, num_steps):
    res = pm.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps=num_steps, init_mesh=3)
    compare_result(res)

@pytest.mark.parametrize('mesh_size', [3, 5, 9])
@pytest.mark.parametrize('num_steps', range(2, 5))
def test_change_mesh(results_equal, num_steps, mesh_size):
    res = pm.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps=num_steps, init_mesh=3)
    res2 = copy.deepcopy(res)
    res2.mesh = [mesh_size] * 3
    res2.mesh = res.mesh
    results_equal(res, res2)

@pytest.mark.parametrize('num_steps_1', range(3))
@pytest.mark.parametrize('num_steps_2', range(3))
def test_restart(num_steps_1, num_steps_2, results_equal):
    num_steps_total = num_steps_1 + num_steps_2
    res = pm.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps = num_steps_total, init_mesh=2)

    res2 = pm.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps = num_steps_1, init_mesh=2)
    res2 = pm.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps = num_steps_total, init_result=res2, init_mesh=2)
    results_equal(res, res2)
    
