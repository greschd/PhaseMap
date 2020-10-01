#!/usr/bin/env python

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import itertools
from addon import util

import numpy as np


def sqr_to_coord(sqr):
    edge, size = sqr.corner, sqr.size
    return [
        edge[0],
        edge[1],
        edge[0] + size,
        edge[1],
        edge[0] + size,
        edge[1] + size,
        edge[0],
        edge[1] + size,
    ]


def plot(sqr_list, max_size, base_mult, AP, savefile="test.svg"):
    mult = base_mult
    max_size *= mult

    col_dict = {None: "red", 0: "green", 1: "blue", 2: "yellow"}

    gp = util.svg.group(stroke="black", stroke_width=1)

    for sqr in sqr_list:
        # flip y-axis
        coord = list(mult * np.array(sqr_to_coord(sqr)))
        for i in range(1, len(coord), 2):
            coord[i] = max_size - coord[i]

        gp.add(
            util.svg.polygon(
                fill=col_dict[sqr.phase],
                points="{},{} {},{} {},{} {},{}".format(*coord),
            )
        )

    for point, val in AP.items():
        pos = np.array(point) * mult
        pos[1] = max_size - pos[1]
        gp.add(util.svg.circle(fill=col_dict[val.phase], cxy=pos, r=3))

    pic = util.svg.canvas(height=max_size, width=max_size)
    pic.add_frame([[(gp, (max_size, max_size))]])
    pic.svg_parse()
    pic.write_svg(savefile)
