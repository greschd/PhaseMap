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

from ._box import PHASE_UNDEFINED


@decorator.decorator
def _plot(func, result, *, ax=None, add_cbar=True, **kwargs):
    # create ax if it does not exist
    if ax is None:
        fig = plt.figure(figsize=[4, 4])
        ax = fig.add_subplot(111)
    # else just get the figure
    else:
        fig = ax.figure

    xlim = [0, 1]
    ylim = [0, 1]
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks(xlim)
    ax.set_yticks(ylim)
    ax.set_xticklabels(result.limits[0])
    ax.set_yticklabels(result.limits[1])

    ax, cmap, norm, vals = func(result, ax=ax, **kwargs)

    if add_cbar:
        fig.subplots_adjust(right=0.9)
        cbar_ax = fig.add_axes([0.95, 0.1, 0.04, 0.8])

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
def boxes(
    result,
    *,
    ax=None,
    scale_val=None,
    plot_undefined=False,
    cmap=None,
    **kwargs
):
    """
    Plots the phase diagram as a collection of boxes, which are colored according to the estimate of the phase in a given box.

    Parameters
    ----------
    result: .Result
        Result of the :func:`.run` phase diagram calculation.
    ax: :py:mod:`matplotlib <matplotlib.pyplot>` ax
        Axes where the plot is drawn.
    add_cbar: bool
        Determines whether a colorbar is added to the figure.
    scale_val: list
        Values to which the colormap is scaled. By default, the colormap is scaled to the set of values which occur in the boxes.
    plot_undefined: bool
        Specifies whether the boxes of undefined phase should be plotted (in white).
    cmap:
        The colormap which is used to plot the phases. The colormap should take values normalized to [0, 1] and return a 4-tuple specifying the RGBA value (again normalized to [0, 1].
    kwargs:
        Keyword arguments passed to :py:class:`matplotlib.patches.Rectangle`.
    """
    if cmap is None:
        # don't do this in the signature, otherwise it gets set at import time
        cmap = plt.get_cmap()

    all_vals = sorted(set(result.points.values())) or [0]
    sqrs = [s for s in result.boxes if s.phase not in (None, PHASE_UNDEFINED)]
    vals = [s.phase for s in sqrs]

    norm = Normalize()
    if scale_val is None:
        norm.autoscale(all_vals)
    else:
        norm.autoscale(scale_val)

    box_colors = cmap([norm(v) for v in vals])

    rect_properties = ChainMap(kwargs, dict(lw=0))
    for color, box in zip(box_colors, sqrs):
        ax.add_patch(
            Rectangle(
                xy=box.corner,
                width=box.size[0],
                height=box.size[1],
                **ChainMap(
                    rect_properties, dict(facecolor=color, edgecolor=color)
                )
            )
        )
    if plot_undefined:
        for box in [b for b in result.boxes if b.phase is PHASE_UNDEFINED]:
            ax.add_patch(
                Rectangle(
                    xy=box.corner,
                    width=box.size[0],
                    height=box.size[1],
                    **ChainMap(rect_properties, dict(facecolor='white'))
                )
            )
    return ax, cmap, norm, all_vals


@export
@_plot
def points(result, *, ax=None, scale_val=None, cmap=None, **kwargs):
    """
    Plots the phase diagram as a collection of boxes, which are colored according to the estimate of the phase in a given box.

    Parameters
    ----------
    result: Result
        Result of the :func:`.run` phase diagram calculation.
    ax: :py:mod:`matplotlib <matplotlib.pyplot>` ax
        Axes where the plot is drawn.
    add_cbar: bool
        Determines whether a colorbar is added to the figure.
    scale_val: list
        Values to which the colormap is scaled. By default, the colormap is scaled to the set of values which occur in the boxes.
    cmap:
        The colormap which is used to plot the phases. The colormap should take values normalized to [0, 1] and return a 4-tuple specifying the RGBA value (again normalized to [0, 1].
    kwargs:
        Keyword arguments passed to :py:meth:`scatter <matplotlib.axes.Axes.scatter>`.
    """
    if cmap is None:
        # don't do this in the signature, otherwise it gets set at import time
        cmap = plt.get_cmap()

    pts = result.points
    all_vals = sorted(set(pts.values())) or [0]

    norm = Normalize()
    if scale_val is None:
        norm.autoscale(all_vals)
    else:
        norm.autoscale(scale_val)

    point_colors = defaultdict(list)
    for coord, phase in pts.items():
        point_colors[cmap(norm(phase))].append(coord)

    for color, coordinates in point_colors.items():
        ax.scatter(*np.array(coordinates).T, color=color, **kwargs)

    return ax, cmap, norm, all_vals
