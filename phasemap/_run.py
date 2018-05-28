import copy
import asyncio
import numbers
import itertools
from fractions import Fraction
from collections import ChainMap

import numpy as np
from fsc.export import export

from ._box import Box, PHASE_UNDEFINED
from ._cache import FuncCache
from ._coordinate import Coordinate
from ._result import Result
from ._logging_setup import LOGGER


@export
def run(fct, limits, init_mesh=5, num_steps=5, init_result=None):
    """Run the PhaseMap algorithm.

    Create an initial set of boxes, and then recursively split boxes of undefined phase until they reach a given minimum size.

    Args:
        fct: The function which evaluates the phase at a given point. Can be either a synchronous or asynchronous (async def) function.
        limits: Boundaries of the region where the phase diagram is evaluated.
        init_mesh: Size of the initial grid, either as an integer, or a list of integers (one for each dimension).
        num_steps: The maximum number of times each box is split.
        init_result: Input result, which is used to cache function evaluations.

    Returns:
        Result: Contains the resulting boxes and points, and the given 'limits'.
    """
    return _RunImpl(
        fct=fct,
        limits=limits,
        init_mesh=init_mesh,
        num_steps=num_steps,
        init_points=getattr(init_result, 'points', None)
    ).execute()


class _RunImpl:
    def __init__(
        self,
        fct,
        limits,
        init_mesh=5,
        num_steps=5,
        init_points=None,
    ):
        self._init_dimensions(
            limits=limits, init_mesh=init_mesh, num_steps=num_steps
        )

        self._func = FuncCache(
            lambda coord: fct(self._coordinate_to_position(coord)),
            data=copy.deepcopy(init_points)
        )
        self.result = Result(
            boxes=set(self._get_initial_boxes()),
            # Note: 'points' needs to be the same object, not a copy. Otherwise
            # it will not update when the '_func' is called.
            points=self._func.data,
            limits=limits
        )

        self._loop = asyncio.get_event_loop()
        self._split_futures_done = dict()
        self._split_futures_pending = dict()
        self._split_futures = ChainMap(
            self._split_futures_pending, self._split_futures_done
        )
        for sqr in self.boxes:
            self._schedule_split_box(sqr)

    def execute(self):
        self._loop.run_until_complete(self._run())
        return self.result

    @property
    def points(self):
        return self.result.points

    @property
    def boxes(self):
        return self.result.boxes

    async def _run(self):
        while not self._check_done():
            await asyncio.sleep(0.)

    def _check_done(self):
        for box, fut in list(self._split_futures_pending.items()):
            if fut.done():
                self._split_futures_pending.pop(box)
                self._split_futures_done[box] = fut
        return not self._split_futures_pending

    def _init_dimensions(self, limits, init_mesh, num_steps):
        self._limit_corner = np.array([low for low, high in limits])
        self._limit_size = np.array([high - low for low, high in limits])
        self._dim = len(limits)

        self._validate_init_mesh(init_mesh)

        self._max_size = Coordinate([
            Fraction(1, m - 1) for m in self._init_mesh
        ])
        self._min_size = self._max_size / 2**num_steps

    def _validate_init_mesh(self, init_mesh):
        if isinstance(init_mesh, numbers.Integral):
            init_mesh = [init_mesh] * self._dim
        else:
            if len(init_mesh) != self._dim:
                raise ValueError(
                    "Length of 'init_mesh' {} does not match the dimension {} of the 'limits'.".
                    format(len(init_mesh), self._dim)
                )
        if any(m < 2 for m in init_mesh):
            raise ValueError('Mesh must be >= 2 for each dimension.')
        self._init_mesh = init_mesh  # pylint: disable=attribute-defined-outside-init

    def _coordinate_to_position(self, coord):
        return self._limit_corner + coord * self._limit_size

    def _get_initial_boxes(self):
        corners = itertools.product(
            *[[i * s for i in range(m - 1)]
              for s, m in zip(self._max_size, self._init_mesh)]
        )
        boxes = [Box(corner=c, size=self._max_size) for c in corners]
        for i, sq1 in enumerate(boxes):
            for sq2 in boxes[i + 1:]:
                sq1.process_possible_neighbour(sq2)
        return boxes

    def _schedule_split_box(self, box):
        if box in self._split_futures:
            return
        if np.all(box.size <= self._min_size):
            return
        fut = asyncio.ensure_future(self._split_box(box), loop=self._loop)
        self._split_futures[box] = fut

    async def _split_box(self, box):
        LOGGER.debug('Splitting {}.'.format(box))
        coordinate_stencil = np.array([[Fraction(1, 2)] * self._dim] + list(
            itertools.product([0, 1], repeat=self._dim)
        ))
        coords = box.corner + coordinate_stencil * box.size
        phases = await asyncio.gather(*[self._func(c) for c in coords])
        corner_stencil = np.array(
            list(itertools.product([0, Fraction(1, 2)], repeat=self._dim))
        )
        new_size = box.size / 2
        new_corners = box.corner + corner_stencil * box.size
        # create new boxes
        new_boxes = [Box(corner=c, size=new_size) for c in new_corners]
        old_neighbours = list(box._neighbours)  # pylint: disable=protected-access
        self.boxes.update(new_boxes)
        # add points to new boxes and neighbours
        for sqr in new_boxes + old_neighbours:
            for c, p in zip(coords, phases):
                sqr.add_point(coord=c, phase=p)
            # add existing points
            for c, p in box._points.items():  # pylint: disable=protected-access
                sqr.add_point(coord=c, phase=p)
            if sqr.phase is PHASE_UNDEFINED:
                self._schedule_split_box(sqr)

        # update neighbour maps
        for new_sq in new_boxes:
            for old_nb in old_neighbours:
                new_sq.process_possible_neighbour(old_nb)
        for i, new_sq1 in enumerate(new_boxes):
            for new_sq2 in new_boxes[i + 1:]:
                new_sq1.process_possible_neighbour(new_sq2)

        # remove old box
        self.boxes.discard(box)
        box.delete_from_neighbours()
