import asyncio
import numbers
import itertools
from fractions import Fraction
from collections import ChainMap

import numpy as np
from fsc.export import export

from ._square import Square, PHASE_UNDEFINED
from ._cache import FuncCache
from ._coordinate import Coordinate
from ._logging_setup import LOGGER


@export
def run(
    fct,
    limits,
    init_mesh=5,
    num_steps=5,
    # all_corners=False,
    # init_result=None
):
    return _RunImpl(
        fct=fct, limits=limits, init_mesh=init_mesh, num_steps=num_steps
    )


class _RunImpl:
    def __init__(
        self,
        fct,
        limits,
        init_mesh=5,
        num_steps=5,
    ):
        self._init_dimensions(
            limits=limits, init_mesh=init_mesh, num_steps=num_steps
        )

        # TODO: Save data in result
        self._func = FuncCache(
            lambda coord: fct(self._coordinate_to_position(coord))
        )
        # TODO: Move to result
        self.squares = set(self._get_initial_squares())

        self._loop = asyncio.get_event_loop()
        self._split_futures_done = dict()
        self._split_futures_pending = dict()
        self._split_futures = ChainMap(
            self._split_futures_pending, self._split_futures_done
        )
        for sq in self.squares:
            self._schedule_split_square(sq)
        self._loop.run_until_complete(self._run())

    # TODO: Move to Result
    @property
    def points(self):
        return self._func.data

    async def _run(self):
        while not self._check_done():
            await asyncio.sleep(2.)

    def _check_done(self):
        for square, fut in list(self._split_futures_pending.items()):
            if fut.done():
                self._split_futures_pending.pop(square)
                self._split_futures_done[square] = fut
        return not self._split_futures_pending

    def _init_dimensions(self, limits, init_mesh, num_steps):
        self._limit_corner = np.array([low for low, high in limits])
        self._limit_size = np.array([high - low for low, high in limits])
        self._dim = len(limits)
        # TODO: Move to Result
        self.limits = limits

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
        self._init_mesh = init_mesh

    def _coordinate_to_position(self, coord):
        return self._limit_corner + coord * self._limit_size

    def _get_initial_squares(self):
        corners = itertools.product(
            *[[i * s for i in range(m - 1)]
              for s, m in zip(self._max_size, self._init_mesh)]
        )
        squares = [Square(corner=c, size=self._max_size) for c in corners]
        for i, sq1 in enumerate(squares):
            for sq2 in squares[i + 1:]:
                sq1.process_possible_neighbour(sq2)
        return squares

    # @FuncCache
    def _schedule_split_square(self, square):
        if square in self._split_futures:
            return
        if np.all(square.size <= self._min_size):
            return
        fut = asyncio.ensure_future(
            self._split_square(square), loop=self._loop
        )
        self._split_futures[square] = fut

    async def _split_square(self, square):
        coordinate_stencil = np.array([[Fraction(1, 2)] * self._dim] + list(
            itertools.product([0, 1], repeat=self._dim)
        ))
        coords = square.corner + coordinate_stencil * square.size
        phases = await asyncio.gather(*[self._func(c) for c in coords])
        corner_stencil = np.array(
            list(itertools.product([0, Fraction(1, 2)], repeat=self._dim))
        )
        new_size = square.size / 2
        new_corners = square.corner + corner_stencil * square.size
        # create new squares
        new_squares = [Square(corner=c, size=new_size) for c in new_corners]
        old_neighbours = list(square.neighbours)
        self.squares.update(new_squares)
        # add points to new squares and neighbours
        for sq in new_squares + old_neighbours:
            for c, p in zip(coords, phases):
                sq.add_point(coord=c, phase=p)
            # add existing points
            for c, p in square._points.items():
                sq.add_point(coord=c, phase=p)
            if sq.phase is PHASE_UNDEFINED:
                self._schedule_split_square(sq)

        # update neighbour maps
        for new_sq in new_squares:
            for old_nb in old_neighbours:
                new_sq.process_possible_neighbour(old_nb)
        for i, new_sq1 in enumerate(new_squares):
            for new_sq2 in new_squares[i + 1:]:
                new_sq1.process_possible_neighbour(new_sq2)

        # remove old square
        self.squares.discard(square)
        square.delete_from_neighbours()
