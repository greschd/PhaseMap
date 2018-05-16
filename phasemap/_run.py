import numbers
import itertools

import numpy as np
from fsc.export import export

from ._container import PhaseMap
from ._logging_setup import logger


@export
def run(
    fct,
    limits,
    init_mesh=5,
    num_steps=5,
    all_corners=False,
    listable=False,
    init_result=None
):
    """
    init_mesh as int -> same in all dimensions. Otherwise as list of int.
    """
    if not listable:
        fct_listable = lambda pts: [fct(p) for p in pts]
    else:
        fct_listable = fct
    # setting up the PhaseMap object
    if isinstance(init_mesh, numbers.Integral):
        init_mesh = [init_mesh] * len(limits)

    result_map = PhaseMap(
        mesh=init_mesh,
        limits=limits,
        all_corners=all_corners,
        init_map=init_result
    )

    # initial calculation
    # calculate for every grid point
    points_frac = result_map.get_initial_points_frac()
    result_map.update(
        points_frac,
        fct_listable([
            result_map.fraction_to_position(pf) for pf in points_frac
        ])
    )
    result_map.create_initial_squares()

    for step in range(num_steps):
        logger.info('starting evaluation step {}'.format(step))
        result_map.decrease_step()
        while not result_map.step_done():
            to_calculate = result_map.pts_to_calculate()
            result_map.update(
                to_calculate,
                fct_listable([
                    result_map.fraction_to_position(pf) for pf in to_calculate
                ])
            )
            result_map.split_all()

    return result_map
