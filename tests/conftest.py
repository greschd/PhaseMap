#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    11.09.2016 13:37:50 CEST
# File:    conftest.py

import json
import operator
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
            request.config.cache.set(full_name, json.loads(json.dumps(data, default=phasemap.io._encoding.encode)))
            raise ValueError('Reference data does not exist.')
        else:
            assert compare_fct(val, json.loads(json.dumps(data, default=phasemap.io._encoding.encode))) # get rid of json-specific quirks
    return inner

@pytest.fixture
def compare_equal(compare_data):
    return lambda data, tag=None: compare_data(operator.eq, data, tag)

@pytest.fixture
def compare_result_old(compare_equal):
    def inner(data, tag=None):
        data = [data.phase.tolist(), data.guess.tolist()]
        return compare_equal(data, tag=tag)
    return inner
    
@pytest.fixture
def compare_result(compare_data, results_equal):
    def inner(data, tag=None):
        return lambda data, tag: compare_data(results_equal, data, tag)
    return inner
    
@pytest.fixture
def results_equal_old():
    def inner(res1, res2):
        assert (res1.phase == res2.phase).all()
        assert (res1.guess == res2.guess).all()
    return inner

@pytest.fixture
def results_equal():
    def inner(res1, res2):
        assert res1._steps == res2._steps
        assert res1.mesh == res2.mesh
        assert sorted(res1.items()) == sorted(res2.items())
        assert res1.dim == res2.dim
        assert res1.limits == res2.limits
    return inner
