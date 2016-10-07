#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    27.09.2016 13:22:14 CEST
# File:    plot.py

from collections import defaultdict, ChainMap

import decorator
import numpy as np
from fsc.export import export

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize, LogNorm, ListedColormap

@decorator.decorator
def _plot(func, phase_map, *, fig=None, ax=None, add_cbar=True, **kwargs):
    if fig is None and ax is None:
        fig = plt.figure(figsize=[4, 4])
    # create ax if it does not exist
    if ax is None:
        ax = fig.add_subplot(111)

    xlim = [0, phase_map.mesh[0] - 1]
    ylim = [0, phase_map.mesh[1] - 1]
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks(xlim)
    ax.set_yticks(ylim)
    ax.set_xticklabels(phase_map.limits[0])
    ax.set_yticklabels(phase_map.limits[1])

    ax, cmap, norm, vals = func(phase_map, ax=ax, **kwargs)

    if add_cbar:
        if fig is None:
            raise ValueError('Colorbar cannot be set when the ax is given explicitly, but the figure is not.')

        fig.subplots_adjust(right=0.9)
        cbar_ax = fig.add_axes([0.95, 0.1, 0.04, 0.8])


        max_val = vals[-1]
        color_vals = [c / max_val for c in vals]
        cbar_cmap = ListedColormap(
            [cmap(v) for v in color_vals]
        )
        c_bar = ColorbarBase(
            cbar_ax,
            cmap=cbar_cmap,
            norm=norm,
            ticks=np.linspace(min(vals), max(vals), 2 * len(vals) + 1)[1::2],
        )
        c_bar.solids.set_edgecolor("k")
        c_bar.set_ticklabels(vals)

    return fig

@export
@_plot
def squares(
        phase_map,
        *,
        ax=None,
        log_norm=False,
        scale_val=None,
        cmap=None,
        fill_lines=False,
        **kwargs
    ):

    if cmap is None:
        # don't do this in the signature, otherwise it gets set at import time
        cmap = plt.get_cmap()

    sqrs = [s for s in phase_map.squares if s.phase is not None]
    vals = [s.phase for s in sqrs]
    all_vals = sorted(set(vals))

    norm = LogNorm() if log_norm else Normalize()
    if scale_val is None:
        norm.autoscale(all_vals)
    else:
        norm.autoscale(scale_val)

    colors = cmap([norm(v) for v in vals])

    rect_properties = ChainMap(
        kwargs,
        dict(lw=1e-11 if fill_lines else 0.)
    )
    for c, s in zip(colors, sqrs):
        ax.add_patch(Rectangle(
            xy=s.corner,
            width=s.size,
            height=s.size,
            **ChainMap(rect_properties, dict(facecolor=c, edgecolor=c))
        ))

    return ax, cmap, norm, all_vals

@export
@_plot
def points(
        phase_map,
        *,
        ax=None,
        log_norm=False,
        scale_val=None,
        cmap=None,
        **kwargs
    ):
    if cmap is None:
        # don't do this in the signature, otherwise it gets set at import time
        cmap = plt.get_cmap()

    pts = phase_map.points
    all_vals = sorted(set([p.phase for p in pts.values()]))

    norm = LogNorm() if log_norm else Normalize()
    if scale_val is None:
        norm.autoscale(all_vals)
    else:
        norm.autoscale(scale_val)


    point_colors = defaultdict(list)
    for p, v in pts.items():
        point_colors[cmap(norm(v.phase))].append(p)

    for c, p in point_colors.items():
        ax.scatter(
            [pt[0] for pt in p],
            [pt[1] for pt in p],
            color=c,
            **kwargs
        )

    return ax, cmap, norm, all_vals

