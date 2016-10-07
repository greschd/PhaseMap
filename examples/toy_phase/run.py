#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    07.10.2016 14:47:06 CEST
# File:    run.py

import sys
import logging

import phasemap as pm

import matplotlib.pyplot as plt
plt.set_cmap('viridis')

logger = logging.getLogger('phasemap')
logger.setLevel(logging.INFO)
DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
logger.addHandler(DEFAULT_HANDLER)

def phase_fct(pos):
    x, y = pos
    if 0 <= x < 0.398:
        if 0.4 < y < 0.6:
            return 1

    if 0.4 < x < 0.6:
        if 0 <= y < 0.6:
            return 1
    if 0.4 < x < 0.6:
        if y >= 0.6:
            return 2

    if 0 <= x < 0.1:
        if y >= 0 and y < 0.1:
            return 1
            
    if (x - 0.5)**2 + (y - 0.5)**2 < 0.1:
        return 3

    return 0 

def plot_squares(num_steps):
    res = pm.get_phase_map(phase_fct, [(0, 1), (0, 1)], num_steps=num_steps, init_mesh=2, listable=False)
    
    pm.plot.squares(res)
    plt.savefig('squares.pdf', bbox_inches='tight')

def plot_points(num_steps):
    res = pm.get_phase_map(phase_fct, [(0, 1), (0, 1)], num_steps=num_steps, init_mesh=2, listable=False)
    
    pm.plot.points(res, s=0.5, lw=0.)
    plt.savefig('points.pdf', bbox_inches='tight')
    
def plot_combined(num_steps):
    res = pm.get_phase_map(phase_fct, [(0, 1), (0, 1)], num_steps=num_steps, init_mesh=2, listable=False)
    
    fig, ax = plt.subplots(figsize=[4.2, 4])
    ax.set_aspect(1.)
    pm.plot.squares(res, ax=ax, zorder=0, add_cbar=False, lw=0.1, edgecolor='k')
    pm.plot.points(res, ax=ax, edgecolors='k', lw=0.1, s=0.5)
    plt.savefig('combined.pdf', bbox_inches='tight')

if __name__ == '__main__':
    plot_squares(8)
    plot_points(8)
    plot_combined(8)

