#!/usr/bin/env python

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import numpy as np

from phasemap import run

run(lambda x: np.sum(x), limits=[(-1, 1)])
