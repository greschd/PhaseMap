#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example shows that the phase must have a starting point in the *interior*
to guarantee convergence.
"""

import phasemap as pm

import matplotlib.pyplot as plt

POINT_SIZE = 1


def phase_fct(pos):
    x, y = pos
    if x == 0:
        if y == 0:
            return 1
        return 0
    m = y / x
    if 0.4 >= m >= 0.1:
        return 1
    if 1.7 >= m >= 1.1:
        return 2
    return 0


def run(num_steps, mesh=2):
    return pm.run(
        phase_fct,
        [(0, 1), (0, 1)],
        num_steps=num_steps,
        mesh=mesh,
        save_interval=0.,
    )


def plot_boxes(res):
    pm.plot.boxes(res)
    plt.savefig('boxes.pdf', bbox_inches='tight')


def plot_points(res):
    pm.plot.points(res, s=POINT_SIZE, lw=0.)
    plt.savefig('points.pdf', bbox_inches='tight')


def plot_combined(res):
    fig, ax = plt.subplots(figsize=[4.2, 4])
    ax.set_aspect(1.)
    pm.plot.boxes(res, ax=ax, zorder=0, add_cbar=False, lw=0.1, edgecolor='k')
    pm.plot.points(res, ax=ax, edgecolors='k', lw=0.1, s=POINT_SIZE)
    plt.savefig('combined.pdf', bbox_inches='tight')


if __name__ == '__main__':
    res = run(5, mesh=2)
    # res = run(5, mesh=3)
    # res = run(5, mesh=4)
    plot_boxes(res)
    plot_points(res)
    plot_combined(res)
