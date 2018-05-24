import pytest
import numpy as np

from phasemap._data_point_cache import DataPointCache


def echo(x):
    return x


def error(x):
    raise ValueError(x)


@pytest.mark.parametrize('vectorized', [True, False])
def test_data_point_cache(vectorized):
    func = DataPointCache(echo, vectorized=vectorized)
    x = np.array(range(10))
    assert np.all(func(x) == x)
    func_error = DataPointCache(error, data=func.data, vectorized=vectorized)
    assert np.all(func_error(x) == x)
    with pytest.raises(ValueError):
        func_error(x + 1)
