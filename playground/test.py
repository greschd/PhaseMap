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
import phasemap2 as pm
import phasemap as pm_old

import matplotlib.pyplot as plt

from plot import plot

from ptools.monitoring import Timer

logger = logging.getLogger('phasemap')
logger.setLevel(logging.INFO)
DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
logger.addHandler(DEFAULT_HANDLER)

def phase_single(x, y):
    if x < 0 or x > 1 :
        return 2
    if y < 0 or y > 1 :
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

    return 0 
    
#~ def phase_fct(x, y):
    #~ return x**2 + y**2 < 1

def phase(val):
    return [phase_fct(v) for v in val]

if __name__ == '__main__':
    plt.set_cmap('viridis')
    NUM_STEPS = 6
    #~ res = pm.get_phase_map(phase, [(-1, 2), (-1, 2)], num_steps=7, init_mesh=4)
    with Timer('foo'):
        res = pm.get_phase_map(phase, [(0, 1), (0, 1)], num_steps=NUM_STEPS, init_mesh=2)
    #~ with Timer('bar'):
        #~ res2 = pm_old.get_phase_map(phase, [(-1, 1), (-1, 1)], num_steps=NUM_STEPS, init_mesh=3)
    #~ A = np.zeros(res.mesh, dtype=int) - 1
    #~ for k, v in res.points.items():
        #~ A[k] = v.phase
    plot(res.squares, res.mesh[0] - 1, 100, res.points)
    print(len(res.points))
    #~ print(len(res2.items()))
    #~ print(res._to_calculate)
    #~ plt.imshow(A.T, interpolation='none', origin='lower')
    #~ plt.colorbar()
    #~ plt.savefig('plot2.pdf', rasterize=False, bbox_inches='tight')
