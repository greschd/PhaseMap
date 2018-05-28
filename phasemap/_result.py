import types


class Result(types.SimpleNamespace):
    def __init__(self, *, points, boxes, limits):  # pylint: disable=useless-super-delegation
        super().__init__(
            points=points,
            boxes=set(boxes),
            limits=[(low, high) for low, high in limits]
        )
