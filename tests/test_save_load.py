#!/usr/bin/env python
# -*- coding: utf-8 -*-

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import tempfile
import json

import pytest
import msgpack

import phasemap as pm

from phases import phase1, phase3


@pytest.mark.parametrize('num_steps', range(2, 5))
@pytest.mark.parametrize('serializer', [json, msgpack])
def test_consistency(results_equal, num_steps, serializer):
    res = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps,
        mesh=3,
    )
    with tempfile.NamedTemporaryFile('w+') as f:
        pm.io.save(res, f.name, serializer=serializer)
        res2 = pm.io.load(f.name, serializer=serializer)
    results_equal(res, res2)


def test_load(results_equal, sample):
    res_loaded = pm.io.load(sample('res.json'))
    res_new = pm.run(phase3, [(0, 1), (0, 1)], num_steps=5, mesh=2)
    results_equal(res_loaded, res_new)
