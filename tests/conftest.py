#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    11.09.2016 13:37:50 CEST
# File:    conftest.py

import json
import operator
import functools
from itertools import zip_longest
from collections.abc import Iterable

import pytest
import numpy as np

import phasemap


@pytest.fixture
def test_name(request):
    """Returns module_name.function_name for a given test"""
    return request.module.__name__ + '/' + request._parent_request._pyfuncitem.name


@pytest.fixture
def compare_data(request, test_name, scope="session"):
    """Returns a function which either saves some data to a file or (if that file exists already) compares it to pre-existing data using a given comparison function."""

    def inner(compare_fct, data, tag=None):
        full_name = test_name + (tag or '')
        val = request.config.cache.get(full_name, None)
        if val is None:
            request.config.cache.set(
                full_name,
                json.
                loads(json.dumps(data, default=phasemap.io._encoding.encode))
            )
            raise ValueError('Reference data does not exist.')
        else:
            val = json.loads(
                json.dumps(val, default=phasemap.io._encoding.encode),
                object_hook=phasemap.io._encoding.decode
            )
            assert compare_fct(
                val,
                json.loads(
                    json.dumps(data, default=phasemap.io._encoding.encode),
                    object_hook=phasemap.io._encoding.decode
                )
            )  # get rid of json-specific quirks

    return inner


@pytest.fixture
def compare_equal(compare_data):
    return lambda data, tag=None: compare_data(operator.eq, data, tag)


@pytest.fixture
def compare_result_equal(compare_data, results_equal):
    return lambda data, tag=None: compare_data(results_equal, data, tag)


@pytest.fixture
def results_equal(squares_idx_equal, squares_equal):
    def inner(res1, res2):
        assert res1.dim == res2.dim
        assert res1.mesh == res2.mesh
        assert res1.limits == res2.limits
        for p in res1.points.keys() | res2.points.keys():
            v1, v2 = res1.points[p], res2.points[p]
            assert v1.phase == v2.phase
            squares_idx_equal(v1.squares, res1, v2.squares, res2)

        squares_equal(res1.squares, res2.squares)
        assert res1.all_corners == res2.all_corners
        squares_idx_equal(res1._split_next, res1, res2._split_next, res2)
        assert res1._to_split == res2._to_split
        assert res1._to_calculate == res2._to_calculate
        return True

    return inner


@pytest.fixture
def squares_idx_equal(normalize_square_idx):
    def inner(squares1, res1, squares2, res2):
        assert normalize_square_idx(squares1, res1) == normalize_square_idx(
            squares2, res2
        )

    return inner


@pytest.fixture
def squares_equal(normalize_squares):
    def inner(squares1, squares2):
        assert normalize_squares(squares1) == normalize_squares(squares2)

    return inner


@pytest.fixture
def normalize_square_idx(normalize_squares):
    def inner(squares, res):
        squares_evaluated = [res.squares[idx] for idx in squares]
        return normalize_squares(squares_evaluated)

    return inner


@pytest.fixture
def normalize_squares():
    def inner(squares):
        return set((s.corner, s.phase, s.size, tuple(sorted(s.points)))
                   for s in squares)

    return inner
