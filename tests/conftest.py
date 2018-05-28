# pylint: disable=unused-argument,redefined-outer-name,protected-access

import os
import json
import operator
from collections import namedtuple

import pytest

import phasemap


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
def results_equal(boxes_equal_from_idx, boxes_equal):
    def inner(res1, res2):
        assert res1.dim == res2.dim
        assert res1.mesh == res2.mesh
        assert res1.limits == res2.limits
        boxes_equal(res1.boxes, res2.boxes)
        for coord in res1.points.keys() | res2.points.keys():
            point1, point2 = res1.points[coord], res2.points[coord]
            assert point1.phase == point2.phase

        boxes_equal_from_idx(
            idx1=res1._split_next, res1=res1, idx2=res2._split_next, res2=res2
        )
        assert res1._to_split == res2._to_split
        assert res1._to_calculate == res2._to_calculate
        return True

    return inner


@pytest.fixture
def boxes_equal_from_idx(normalize_boxes_from_idx):
    def inner(idx1, res1, idx2, res2):
        assert normalize_boxes_from_idx(idx1,
                                        res1) == normalize_boxes_from_idx(
                                            idx2, res2
                                        )

    return inner


NormalizedBox = namedtuple('NormalizedBox', ['corner', 'phase', 'size'])


@pytest.fixture
def boxes_equal(normalize_boxes):
    def inner(boxes1, boxes2):
        assert normalize_boxes(boxes1) == normalize_boxes(boxes2)

    return inner


@pytest.fixture
def normalize_boxes_from_idx(normalize_boxes):
    def inner(idx, res):
        boxes_evaluated = [res.boxes[i] for i in idx]
        return normalize_boxes(boxes_evaluated)

    return inner


@pytest.fixture
def normalize_boxes():
    def inner(boxes):
        return set(
            NormalizedBox(
                corner=s.corner,
                phase=s.phase,
                size=s.size,
            ) for s in boxes
        )

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
