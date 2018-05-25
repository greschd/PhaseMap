import numpy as np
from fsc.export import export

NOT_FOUND = object()


@export
class DataPointCache:
    def __init__(self, func, data=None):
        self.func = func
        if data is None:
            self.data = dict()
        else:
            self.data = data

    def __call__(self, coord):
        try:
            return self.data[coord]
        except KeyError:
            result = self.func(coord)
            self.data[coord] = result
            return result
