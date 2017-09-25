#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    27.09.2016 13:22:14 CEST
# File:    plot.py
"""
This module contains functions for plotting the phase diagram. The functions are based upon the :py:mod:`matplotlib <matplotlib.pyplot>` package.
"""

from collections import defaultdict, ChainMap

import decorator
import numpy as np
from fsc.export import export

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize, ListedColormap


@decorator.decorator
def _plot(func, phase_map, *, axes=None, add_cbar=True, **kwargs):
    # create axes if it does not exist
    if axes is None:
        fig = plt.figure(figsize=[4, 4])
        axes = fig.add_subplot(111)
    # else just get the figure
    else:
        fig = axes.figure

    xlim = [0, phase_map.mesh[0] - 1]
    ylim = [0, phase_map.mesh[1] - 1]
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    axes.set_xticks(xlim)
    axes.set_yticks(ylim)
    axes.set_xticklabels(phase_map.limits[0])
    axes.set_yticklabels(phase_map.limits[1])

    axes, cmap, norm, vals = func(phase_map, axes=axes, **kwargs)

    if add_cbar:
        fig.subplots_adjust(right=0.9)
        cbar_ax = fig.add_axes([0.95, 0.1, 0.04, 0.8])

        max_val = vals[-1]
        color_vals = [norm(c) for c in vals]
        cbar_cmap = ListedColormap([cmap(v) for v in color_vals])
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
    axes=None,
    add_cbar=True,
    scale_val=None,
    cmap=None,
    **kwargs
):
    """
    Plots the phase diagram as a collection of squares, which are colored according to the estimate of the phase in a given square.

    :param phase_map: Result of the phase mapping run.
    :type phase_map: :class:`.PhaseMap`

    :param axes: Axes where the plot is drawn.
    :type axes: :py:mod:`matplotlib <matplotlib.pyplot>` axes

    :param add_cbar: Determines whether a colorbar is added to the figure.
    :type add_cbar: bool

    :param scale_val: Values to which the colormap is scaled. By default, the colormap is scaled to the set of values which occur in the squares.
    :type scale_val: list

    :param cmap: The colormap which is used to plot the phases. The colormap should take values normalized to [0, 1] and return a 4-tuple specifying the RGBA value (again normalized to [0, 1].

    :param kwargs: Keyword arguments passed to :py:class:`matplotlib.patches.Rectangle`.
    """
    if cmap is None:
        # don't do this in the signature, otherwise it gets set at import time
        cmap = plt.get_cmap()

    sqrs = [s for s in phase_map.squares if s.phase is not None]
    vals = [s.phase for s in sqrs]
    all_vals = sorted(set(vals))

    norm = Normalize()
    if scale_val is None:
        norm.autoscale(all_vals)
    else:
        norm.autoscale(scale_val)

    colors = cmap([norm(v) for v in vals])

    rect_properties = ChainMap(kwargs, dict(lw=0))
    for c, s in zip(colors, sqrs):
        axes.add_patch(
            Rectangle(
                xy=s.corner,
                width=s.size,
                height=s.size,
                **ChainMap(rect_properties, dict(facecolor=c, edgecolor=c))
            )
        )

    return axes, cmap, norm, all_vals


@export
@_plot
def points(
    phase_map,
    *,
    axes=None,
    add_cbar=True,
    scale_val=None,
    cmap=None,
    **kwargs
):
    """
    Plots the phase diagram as a collection of squares, which are colored according to the estimate of the phase in a given square. TODO: FIX!!!!!

    :param axes: Axes where the plot is drawn.
    :type axes: :py:mod:`matplotlib <matplotlib.pyplot>` axes

    :param add_cbar: Determines whether a colorbar is added to the figure.
    :type add_cbar: bool

    :param scale_val: Values to which the colormap is scaled. By default, the colormap is scaled to the set of values which occur in the squares.
    :type scale_val: list

    :param cmap: The colormap which is used to plot the phases. The colormap should take values normalized to [0, 1] and return a 4-tuple specifying the RGBA value (again normalized to [0, 1].

    :param kwargs: Keyword arguments passed to :py:meth:`scatter <matplotlib.axes.Axes.scatter>`.
    """
    if cmap is None:
        # don't do this in the signature, otherwise it gets set at import time
        cmap = plt.get_cmap()

    pts = phase_map.points
    all_vals = sorted(set([p.phase for p in pts.values()]))

    norm = Normalize()
    if scale_val is None:
        norm.autoscale(all_vals)
    else:
        norm.autoscale(scale_val)

    point_colors = defaultdict(list)
    for p, v in pts.items():
        point_colors[cmap(norm(v.phase))].append(p)

    for c, p in point_colors.items():
        axes.scatter([pt[0] for pt in p], [pt[1] for pt in p],
                     color=c,
                     **kwargs)

    return axes, cmap, norm, all_vals
