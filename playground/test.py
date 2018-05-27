#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.08.2016 04:11:07 CEST
# File:    test.py

import sys
import copy
import logging

import numpy as np
import phasemap as pm

import matplotlib.pyplot as plt
plt.set_cmap('viridis')
from matplotlib.colors import ListedColormap

from plot import plot
from ptools.advanced_plot import cmap_irregular
from ptools.monitoring import Timer

logger = logging.getLogger('phasemap')
logger.setLevel(logging.INFO)
DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
logger.addHandler(DEFAULT_HANDLER)


def phase_single(x, y):
    if x < 0 or x > 1:
        return 2
    if y < 0 or y > 1:
        return 2
    if 0.4 < y < 0.6 and x < 0.35:
        return 1
    if 0.4 < x < 0.6:
        if y < 0.65:
            return 1
        return 2
    if x < 0.1 and y < 0.1:
        return 1

    return 0


#~ def phase_single(x, y):
#~ if x < 0 or x > 1 :
#~ return 2
#~ if y < 0 or y > 1 :
#~ return 2
#~ if  y < 0.5 and x < 0.5:
#~ return 1
#~ return 0
#~ def phase_single(x, y):
#~ if 0.48 < y < 0.6 and x < 0.35:
#~ return 1
#~ if 0.4 < x  and y < 0.65:
#~ return 1
#~ if  0.24 < y < 0.26 and x < 0.1:
#~ return 1

#~ return 0


def phase_fct(pos):
    if pos[0] >= 0 and pos[0] < 0.3:
        if pos[1] > 0.4 and pos[1] < 0.6:
            return 1

    if pos[0] > 0.4 and pos[0] < 0.6:
        if pos[1] >= 0 and pos[1] < 0.6:
            return 1
    if pos[0] > 0.4 and pos[0] < 0.6:
        if pos[1] >= 0.6:
            return 2

    if pos[0] >= 0 and pos[0] < 0.1:
        if pos[1] >= 0 and pos[1] < 0.1:
            return 1

    if (pos[0] - 0.5)**2 + (pos[1] - 0.5)**2 < 0.1:
        return 3

    return 0


#~ def phase_fct(x, y):
#~ return x**2 + y**2 < 1

#~ def phase_fct(x, y):
#~ return (x**2 + y**2) < 1
#~ def phase_fct(x, y, z=0):
#~ return x**2 + y**2 + z**2  < 1
#~ def phase_fct(x, y, z=0):
#~ if x < 1 / np.pi and y < 1 / np.pi:
#~ return 0
#~ elif x < 1 / np.pi:
#~ return 1
#~ return 2

#~ def phase(val):
#~ return [phase_fct(v) for v in val]

#~ def phase(val):
#~ x, y = val
#~ if 0.2 < y < 0.3 and 0.1 < x < 0.6:
#~ return 1
#~ if y < 0.25 and x < 0.15:
#~ return 1
#~ return 0
#~ def phase(val):
#~ x, y = val
#~ return 1 if x**2 + y**2 < 1 else 0
#~ print(val)
#~ if val in [[0., 0.], [0.25, 0.25], [0.5, 0.125]]:
#~ return 1
#~ elif val in [[0.375, 0.125], [0.5, 0.125]]:
#~ return 2
#~ return 0

if __name__ == '__main__':

    NUM_STEPS = 10
    res = pm.get_phase_map(
        phase_fct,
        [(0, 1), (0, 1)],
        num_steps=NUM_STEPS,
        init_mesh=2,
    )

    BORDEAUX = '#770044'
    GREY = '#AAAAAA'
    BLUE = '#003399'
    GREEN = '#008833'
    ORANGE = '#EE6600'
    cmap = ListedColormap([GREY, BORDEAUX, BLUE, ORANGE])
    pm.plot.squares(res, cmap=cmap)
    plt.savefig('foo.pdf', bbox_inches='tight')
