import numpy as np
from fsc.export import export

NOT_FOUND = object()

@export
class DataPointCache:
    def __init__(self, func, data=None, listable=False):
        if data is None:
            self.data = dict()
        else:
            self.data = data

        if not listable:
            self.func = lambda coord_array: np.array([func(coord) for coord in coord_array])
        else:
            self.func = func

    def __call__(self, coord_array):
        result = np.array([self.data.get(coord, NOT_FOUND) for coord in coord_array])
        cache_miss_idx = np.nonzero(result == NOT_FOUND)[0]
        if cache_miss_idx.size > 0:
            missing_coord = coord_array[cache_miss_idx]
            result_new = self.func(missing_coord)
            self.data.update({c: r for c, r in zip(missing_coord, result_new)})
            result[cache_miss_idx] = result_new
        return result
