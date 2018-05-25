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

import phasemap as pm

from phases import phase1, phase2


@pytest.mark.parametrize('num_steps', range(2, 5))
@pytest.mark.parametrize('serializer', [json, msgpack, pickle])
def test_consistency(results_equal, num_steps, serializer):
    res = pm.run(
        phase1, [(-1, 1), (-1, 1)],
        num_steps=num_steps,
        init_mesh=3,
    )
    with tempfile.NamedTemporaryFile('w+') as f:
        pm.io.save(res, f.name, serializer=serializer)
        res2 = pm.io.load(f.name, serializer=serializer)
    results_equal(res, res2)


def test_load(results_equal, sample):
    res_loaded = pm.io.load(sample('res.json'))
    res_new = pm.run(
        phase2, [(0, 1), (0, 1)], num_steps=5, init_mesh=2
    )
    results_equal(res_loaded, res_new)
