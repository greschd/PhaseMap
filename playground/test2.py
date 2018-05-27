#!/usr/bin/env python

import numpy as np

from phasemap import run

run(lambda x: np.sum(x), limits=[(-1, 1)])
