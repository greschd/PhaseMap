#!/usr/bin/env python

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import numpy as np
import scipy.misc
import phasemap2 as pm

import matplotlib.pyplot as plt

# ~ def circle(x, y):
# ~ return 1 if x**2 + y**2 < 1 else 0

# ~ def wedge(x, y):
# ~ return 1 if (y - abs(x)) > 0 and (x**2 + y**2 < 1) else 0

# ~ def phase(val):
# ~ return [wedge(x, y) + circle(x, y) for x, y in val]


def rhombus(x, y):
    return 1 if (abs(x) + abs(y) < 1) else 0


def circle2(x, y, r=1):
    return 1 if (x ** 2 + y ** 2) < r ** 2 else 0


# ~ def box(x, y, l=0.5):
# ~ return 1 if (-l < x < l) and (-l < y < l) else 0


def phase(val):
    return [rhombus(x, y) + circle2(x, y, r=np.sqrt(0.5)) for x, y in val]


# ~ def phase(val):
# ~ return [rhombus(x, y) for x, y in val]

if __name__ == "__main__":
    plt.set_cmap("viridis")
    res = pm.get_phase_map(phase, [(-1.1, 1.1), (-1.1, 1.1)], num_steps=6, mesh=3)
    A = np.zeros(res.mesh, dtype=int) - 1
    for k, v in res.items():
        A[k] = v
    B = np.zeros(res.mesh, dtype=int) - 1
    for k, v in res.items():
        B[k] = v
    for i in range(B.shape[0]):
        iterator = range(B.shape[1])
        if i % 2 == 1:
            iterator = reversed(iterator)
        for j in iterator:
            if B[i, j] == -1:
                B[i, j] = current
            else:
                current = B[i, j]
    color_mapping_1 = {
        -1: [0, 0, 0],
        0: [0x00, 0x00, 0x00],
        1: [0, 0x33, 0x99],
        2: [0xEE, 0x66, 0],
    }
    color_mapping_2 = {
        -1: [0, 0, 0],
        0: [0xFF, 0xFF, 0xFF],
        1: [0, 0x1F, 0x5C],
        2: [0xC2, 0x3B, 5],
    }
    A = np.zeros(tuple(list(res.mesh) + [3]), dtype=int)
    for i, line in enumerate(B):
        for j, elem in enumerate(line):
            A[i, j] = color_mapping_1[elem]
    for k, v in res.items():
        A[k] = color_mapping_2[v]

    scipy.misc.imsave("logo_out.png", A, format="png")
