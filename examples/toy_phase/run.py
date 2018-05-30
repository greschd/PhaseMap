#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    07.10.2016 14:47:06 CEST
# File:    run.py

import os
import sys
import logging

import phasemap as pm

import matplotlib.pyplot as plt
plt.set_cmap('viridis')

POINT_SIZE = 1


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
            return -2

    if 0 <= x < 0.1:
        if y >= 0 and y < 0.1:
            return 1

    if (x - 0.5)**2 + (y - 0.5)**2 < 0.1:
        return 3

    return 0


def run(num_steps):
    os.makedirs('results', exist_ok=True)
    return pm.run(
        phase_fct,
        [(0, 1), (0, 1)],
        num_steps=num_steps,
        mesh=2,
        save_file='results/res_{}.json',
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
    res = run(8)
    plot_boxes(res)
    plot_points(res)
    plot_combined(res)
