# -*- coding: utf-8 -*-

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

# pylint: disable=unused-argument,redefined-outer-name,protected-access

import os
import json
import operator

import pytest

import phasemap


def pytest_addoption(parser):
    parser.addoption(
        '--no-plot-tests', action='store_true', help='disable the plot tests'
    )


def pytest_configure(config):
    # register additional marker
    config.addinivalue_line("markers", "plot: mark tests which create plots")


def pytest_runtest_setup(item):
    try:
        plot_marker = item.get_marker("plot")
    except AttributeError:
        plot_marker = item.get_closest_marker("plot")
    if plot_marker is not None:
        if item.config.getoption("--no-plot-tests"):
            pytest.skip("Skipping plot tests.")


@pytest.fixture
def test_name(request):
    """Returns module_name.function_name for a given test"""
    return request.module.__name__ + '/' + request._parent_request._pyfuncitem.name  # pylint: disable=protected-access


@pytest.fixture
def compare_data(request, test_name, scope="session"):
    """Returns a function which either saves some data to a file or (if that file exists already) compares it to pre-existing data using a given comparison function."""
    def inner(compare_fct, data, tag=None):
        full_name = test_name + (tag or '')
        val = request.config.cache.get(full_name, None)
        if val is None:
            request.config.cache.set(
                full_name,
                json.loads(
                    json.dumps(data, default=phasemap.io._encoding.encode)
                )
            )
            raise ValueError('Reference data does not exist.')
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
def results_equal(boxes_equal):
    def inner(res1, res2):
        assert res1.limits == res2.limits
        boxes_equal(res1.boxes, res2.boxes)
        assert res1.points == res2.points

        return True

    return inner


@pytest.fixture
def boxes_equal():
    def inner(boxes1, boxes2):
        assert boxes1 == boxes2
        box2_lookup = {b: b for b in boxes2}
        for box1 in boxes1:
            assert box1.phase == box2_lookup[box1].phase

    return inner


@pytest.fixture
def sample():
    def inner(name):
        return os.path.join(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'samples'
            ), name
        )

    return inner
