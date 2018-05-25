import pytest
import numpy as np

from phasemap._data_point_cache import DataPointCache


def echo(x):
    return x


def error(x):
    raise ValueError(x)


def test_data_point_cache():
    func = DataPointCache(echo)
    for x in range(10):
        assert x == func(x)
    func_error = DataPointCache(error, data=func.data)
    for x in range(10):
        assert x == func_error(x)
    with pytest.raises(ValueError):
        func_error(10)
