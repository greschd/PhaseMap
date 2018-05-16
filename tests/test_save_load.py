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


def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0


def line(x, y):
    return 1 if x > 0.5 or y < 0.2 else 0


def phase(val):
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

    if (pos[0] - 0.5)**2 + (pos[1] - 0.5)**2 < 0.1:
        return 3

    return 0


@pytest.mark.parametrize('num_steps', range(2, 5))
@pytest.mark.parametrize('serializer', [json, msgpack, pickle])
def test_consistency(results_equal, num_steps, serializer):
    res = pm.run(
        phase, [(-1, 1), (-1, 1)],
        num_steps=num_steps,
        init_mesh=3,
        listable=True
    )
    with tempfile.NamedTemporaryFile('w+') as f:
        pm.io.save(res, f.name, serializer=serializer)
        res2 = pm.io.load(f.name, serializer=serializer)
    results_equal(res, res2)


def test_load(results_equal, sample):
    res_loaded = pm.io.load(sample('res.json'))
    res_new = pm.run(
        phase2, [(0, 1), (0, 1)], num_steps=5, init_mesh=2, listable=False
    )
    results_equal(res_loaded, res_new)
