import types


class Result(types.SimpleNamespace):
    def __init__(self, *, points, squares, limits):  # pylint: disable=useless-super-delegation
        super().__init__(points=points, squares=squares, limits=limits)
