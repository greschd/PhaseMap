#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.08.2016 04:11:07 CEST
# File:    test.py

import tempfile
import json
import pickle

import pytest
import msgpack
import phasemap_old as pmo

def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0

def line(x, y):
    return 1 if x > 0.5 or y < 0.2 else 0

def phase(val):
    return [line(x, y) + circle(x, y) for x, y in val]

#~ @pytest.mark.parametrize('num_steps', range(2, 5))
#~ @pytest.mark.parametrize('serializer', [json, msgpack, pickle])
#~ def test_consistency_old(results_equal_old, num_steps, serializer):
    #~ res = pmo.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps=num_steps, init_mesh=3)
    #~ with tempfile.NamedTemporaryFile('w+') as f:
        #~ pmo.io.save(res, f.name, serializer=serializer)
        #~ res2 = pmo.io.load(f.name, serializer=serializer)

