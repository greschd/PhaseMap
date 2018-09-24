import copy
import asyncio
import numbers
import itertools
from fractions import Fraction
from collections import ChainMap

import numpy as np
from fsc.export import export
from fsc.async_tools import PeriodicTask

from . import io as _io
from ._box import Box, PHASE_UNDEFINED
from ._cache import FuncCache
from ._coordinate import Coordinate
from ._result import Result
from ._logging_setup import LOGGER


@export
def run(  # pylint: disable=too-many-arguments
    fct,
    limits,
    mesh=5,
    num_steps=5,
    all_corners=False,
    init_result=None,
    save_file=None,
    load=False,
    load_quiet=True,
    serializer='auto',
    save_interval=5.,
):
    """Run the PhaseMap algorithm.

    Create an initial set of boxes, and then recursively split boxes of undefined phase until they reach a given minimum size.

    Parameters
    ----------
    fct:
        The function which evaluates the phase at a given point. Can be either a synchronous or asynchronous (async def) function.
    limits:
        Boundaries of the region where the phase diagram is evaluated.
    mesh:
        Size of the initial grid, either as an integer, or a list of integers (one for each dimension).
    num_steps: int
        The maximum number of times each box is split.
    all_corners: bool
        Determines whether all corners of a box should be calculated, or only the vertices and middle point of the parent box.
    init_result: Result
        Input result, which is used to cache function evaluations.
    save_file: str
        Path of the file where the intermediate results should be stored. A format string can also be passed, and will be formatted with an incrementing index.
    load: bool
        Determines whether the initial result is loaded from the ``save_file``.
    load_quiet: bool
        Determines if the error is suppressed when the initial result cannot be loaded from the ``save_file``.
    serializer: module
        Serializer used to save and load the result.
    save_interval: float
        Minimum time between saving the result.

    Returns
    -------
    Result:
        Contains the resulting boxes and points, and the given 'limits'.
    """
    if save_file is not None and load:
        if init_result is not None:
            raise ValueError(
                "Inconsistent input: 'init_result' and 'load' cannot be set simultaneously."
            )
        try:
            init_result = _io.load(save_file, serializer=serializer)
        except IOError as err:
            if not load_quiet:
                raise err

    if init_result is not None:
        if not np.allclose(limits, init_result.limits):
            raise ValueError(
                "Limits {} of the 'init_result' do not match the given limits {}"
                .format(init_result.limits, limits)
            )
        init_points = init_result.points
    else:
        init_points = None

    return _RunImpl(
        fct=fct,
        limits=limits,
        mesh=mesh,
        num_steps=num_steps,
        all_corners=all_corners,
        init_points=init_points,
        save_file=save_file,
        serializer=serializer,
        save_interval=save_interval,
    ).execute()


class _RunImpl:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        fct,
        limits,
        mesh=5,
        num_steps=5,
        all_corners=False,
        init_points=None,
        save_file=None,
        serializer='auto',
        save_interval=5.,
    ):
        self._save_file = save_file
        self._serializer = serializer
        self._save_interval = save_interval
        self._save_count = 0
        self._squares_need_saving = False
        self._init_dimensions(limits=limits, mesh=mesh, num_steps=num_steps)
        self._all_corners = all_corners

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
        for sqr in self.result.boxes:
            self._schedule_split_box(sqr)

    @property
    def needs_saving(self):
        return self._squares_need_saving or self._func.needs_saving

    @needs_saving.setter
    def needs_saving(self, value):
        self._squares_need_saving = value
        self._func.needs_saving = value

    def execute(self):
        self._loop.run_until_complete(self._run())
        return self.result

    async def _run(self):
        async with PeriodicTask(self._save, delay=self._save_interval):
            while not self._check_done():
                await asyncio.sleep(0.)

    def _check_done(self):
        done_tasks = [(box, fut)
                      for (box, fut) in self._split_futures_pending.items()
                      if fut.done()]

        # Retrieve all exceptions to avoid asyncio 'exception never retrieved'
        # warning, but can only raise one.
        exceptions = [fut.exception() for _, fut in done_tasks]
        exceptions = [exc for exc in exceptions if exc is not None]
        if exceptions:
            raise exceptions[0]

        for box, fut in done_tasks:
            self._split_futures_pending.pop(box)
            self._split_futures_done[box] = fut
        return not self._split_futures_pending

    def _init_dimensions(self, limits, mesh, num_steps):
        self._limit_corner = np.array([low for low, high in limits])
        self._limit_size = np.array([high - low for low, high in limits])
        self._dim = len(limits)

        self._validate_mesh(mesh)

        self._max_size = Coordinate([Fraction(1, m - 1) for m in self._mesh])
        self._min_size = self._max_size / 2**num_steps

    def _validate_mesh(self, mesh):
        if isinstance(mesh, numbers.Integral):
            mesh = [mesh] * self._dim
        else:
            if len(mesh) != self._dim:
                raise ValueError(
                    "Length of 'mesh' {} does not match the dimension {} of the 'limits'."
                    .format(len(mesh), self._dim)
                )
        if any(m < 2 for m in mesh):
            raise ValueError('Mesh must be >= 2 for each dimension.')
        self._mesh = mesh  # pylint: disable=attribute-defined-outside-init

    def _coordinate_to_position(self, coord):
        return self._limit_corner + coord * self._limit_size

    def _get_initial_boxes(self):
        corners = itertools.product(
            *[[i * s for i in range(m - 1)]
              for s, m in zip(self._max_size, self._mesh)]
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
        if self._all_corners:
            coordinate_stencil = np.array(
                list(
                    itertools.product([0, Fraction(1, 2), 1], repeat=self._dim)
                )
            )
        else:
            coordinate_stencil = np.array(
                [[Fraction(1, 2)] * self._dim] +
                list(itertools.product([0, 1], repeat=self._dim))
            )
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
        self.result.boxes.update(new_boxes)
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
                new_sq1.process_certain_neighbour(new_sq2)

        # remove old box
        self.result.boxes.discard(box)
        box.delete_from_neighbours()
        self.needs_saving = True

    def _save(self):
        if self._save_file is None:
            return
        if self.needs_saving:
            _io.save(
                self.result,
                self._save_file.format(self._save_count),
                serializer=self._serializer
            )
            self._save_count += 1
            self.needs_saving = False
