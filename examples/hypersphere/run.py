# -*- coding: utf-8 -*-

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import phasemap as pm


def phase(pos):
    """
    Defines an n-dimensional hypersphere.
    """
    return int(sum(x**2 for x in pos) <= 1)


def run_calc(dim, num_steps, all_corners=False):
    res = pm.run(
        phase,
        limits=[(-1.1, 1.1)] * dim,
        num_steps=num_steps,
        mesh=3,
        all_corners=all_corners
    )
    return res


if __name__ == '__main__':
    for i in [1, 2, 3]:
        for n in range(1, 5):
            for all_corners in [False, True]:
                print(
                    i, n, all_corners, len(run_calc(i, n, all_corners).points)
                )
