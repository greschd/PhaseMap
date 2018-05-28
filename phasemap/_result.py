import types


class Result(types.SimpleNamespace):
    def __init__(self, *, points, boxes, limits):  # pylint: disable=useless-super-delegation
        super().__init__(points=points, boxes=boxes, limits=limits)
