import pytest
import numpy as np

from phasemap._cache import FuncCache


def echo(x):
    return x


def error(x):
    raise ValueError(x)


def test_func_cache():
    func = FuncCache(echo)
    for x in range(10):
        assert x == func(x)
    func_error = FuncCache(error, data=func.data)
    for x in range(10):
        assert x == func_error(x)
    with pytest.raises(ValueError):
        func_error(10)
