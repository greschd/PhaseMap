# -*- coding: utf-8 -*-

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import types


class Result(types.SimpleNamespace):
    """
    Container class for the result of a :func:`.run` calculation. Contains the boxes, points and limits of the calculation.
    """

    def __init__(self, *, points, boxes, limits):  # pylint: disable=useless-super-delegation
        super().__init__(
            points=points,
            boxes=set(boxes),
            limits=[(low, high) for low, high in limits]
        )
