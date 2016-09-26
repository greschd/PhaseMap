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

def phase(val):
    return [line(x, y) + circle(x, y) for x, y in val]
    
@pytest.mark.parametrize('num_steps', range(2, 5))
@pytest.mark.parametrize('all_corners', [False, True])
def test_phase(compare_equal, num_steps, all_corners):
    res = pm.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps=num_steps, init_mesh=3, all_corners=all_corners)
    compare_equal(sorted([(k, v.phase) for k, v in res.points.items()]))
    # This can be used when the code is stable and io is done
    #~ compare_result(res)
