import numbers
from fractions import Fraction

import numpy as np
from fsc.export import export

from ._square import Square
from ._logging_setup import LOGGER


@export
def run(
    fct,
    limits,
    init_mesh=5,
    num_steps=5,
    all_corners=False,
    init_result=None
):
    if isinstance(init_mesh, numbers.Integral):
        init_mesh = [init_mesh] * len(limits)
    if any(m < 2 for m in init_mesh):
        raise ValueError('Mesh must be >= 2 for each dimension.')
    dim = len(init_mesh)


def _get_initial_squares(init_mesh):
    size = np.array([Fraction(1, m - 1) for m in init_mesh])
    corners = itertools.product(*[
        [i * s for i in range(m)] for s, m in zip(size, init_mesh)
    ])
    squares = [Square(corner=c, size=s) for c, s in zip(corners, size)]
    for i, sq1 in enumerate(squares):
        for sq2 in squares[i + 1:]:
            sq1.process_possible_neighbour(sq2)
    return squares
