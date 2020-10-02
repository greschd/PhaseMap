# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>
"""Tests for the plot functions."""
# pylint: disable=redefined-outer-name,unused-wildcard-import

import pytest
import matplotlib

matplotlib.use("Agg")

from phases import phase3
from plottest_helpers import *

import phasemap as pm


@pytest.mark.plot
@pytest.mark.parametrize("scale_val", [None, (-3, 3)])
@pytest.mark.parametrize("plot_fct", [pm.plot.boxes, pm.plot.points])
def test_plots(assert_image_equal, plot_fct, scale_val):
    res = pm.run(
        phase3,
        limits=[(0, 1)] * 2,
        num_steps=2,
    )
    plot_fct(res, scale_val=scale_val)
    assert_image_equal()
