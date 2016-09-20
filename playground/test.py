#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.08.2016 04:11:07 CEST
# File:    test.py

import copy

import numpy as np
import phasemap2 as pm

import matplotlib.pyplot as plt

def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0

def line(x, y):
    return 1 if x > 0.5 or y < 0.2 else 0

def phase(val):
    return [line(x, y) + circle(x, y) for x, y in val]

if __name__ == '__main__':
    plt.set_cmap('viridis')
    res = pm.get_phase_map(phase, [(-1.1, 1.1), (-1.1, 1.1)], num_steps=7, init_mesh=3)
    A = np.zeros(res.mesh, dtype=int) - 1
    for k, v in res.items():
        A[k] = v
    plt.imshow(A.T, interpolation='none', origin='lower')
    plt.colorbar()
    plt.savefig('plot_start.pdf', rasterize=False, bbox_inches='tight')
    #~ plt.clf()
    #~ for i in range(res.mesh[0]):
        #~ iterator = range(res.mesh[1])
        #~ if i % 2 == 1:
            #~ iterator = reversed(iterator)
        #~ for j in iterator:
            #~ if A[i, j] == -1:
                #~ A[i, j] = current
            #~ else:
                #~ current = A[i, j]
    #~ A[0,0] = -1
    #~ plt.imshow(A.T, interpolation='none', origin='lower')
    #~ plt.colorbar()
    #~ plt.savefig('plot.svg', bbox_inches='tight')
    

