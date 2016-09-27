#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    27.09.2016 13:22:14 CEST
# File:    plot.py

import decorator
import numpy as np
from fsc.export import export

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize, LogNorm, ListedColormap

@decorator.decorator
def _plot(func, phase_map, *, axis=None, **kwargs):
    # create axis if it does not exist
    if axis is None:
        return_fig = True
        fig = plt.figure(figsize=[4, 4])
        axis = fig.add_subplot(111)
    else:
        return_fig = False

    xlim = [0, phase_map.mesh[0] - 1]
    ylim = [0, phase_map.mesh[1] - 1]
    axis.set_xlim(xlim)
    axis.set_ylim(ylim)
    axis.set_xticks(xlim)
    axis.set_yticks(ylim)
    axis.set_xticklabels(phase_map.limits[0])
    axis.set_yticklabels(phase_map.limits[1])

    axis, cmap, norm, vals = func(phase_map, axis=axis, **kwargs)

    if return_fig:
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
        axis=None, 
        log_norm=False, 
        scale_val=None,
        cmap=None,
        unknown_value=None,
        phase_mapping=None,
        fill_lines=False
    ):
    
    # phase_mapping can be used for non-numeric phases
    if phase_mapping is None:
        phase_mapping = lambda x: x
    if cmap is None:
        # don't do this in the signature, otherwise it gets set at import time
        cmap = plt.get_cmap()
    
    squares = phase_map.squares
    if unknown_value is None:
        squares = [s for s in squares if s.phase is not None]
    vals = [s.phase if s.phase is not None else unknown_value for s in squares]
    all_vals = sorted(set([phase_mapping(v.phase) for v in phase_map.points.values()]))
    
    
    if log_norm:
        norm = LogNorm()
    else:
        norm = Normalize()
    if scale_val is None:
        norm.autoscale(all_vals)
    else:
        norm.autoscale(scale_val)

    colors = cmap([norm(v) for v in vals])
    
    for c, s in zip(colors, squares):
        axis.add_patch(Rectangle(
            xy=s.corner,
            width=s.size,
            height=s.size,
            color=c,
            lw=1e-11 if fill_lines else 0.,
        ))
        
    return axis, cmap, norm, all_vals

