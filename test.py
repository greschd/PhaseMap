#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.08.2016 04:11:07 CEST
# File:    test.py

import numpy as np
from phasemap import *
import matplotlib.pyplot as plt

def circle(x, y):
    return 2 if x**2 + y**2 < 1 else 0

def line(x, y):
    return 1 if x > 0.5 else 0

def phase(val):
    return [line(x, y) + circle(x, y) for x, y in val]

res = get_phase_map(phase, [(0, 1), (0, 1)], num_steps=0, init_mesh=3)
#~ print(res.phase)
#~ print(res.result.flatten())
res = get_phase_map(phase, [(0, 1), (0, 1)], num_steps=5, init_mesh=3)
print([v for v in res.result.flatten()])
print([v.phase for v in res.result.flatten()])
#~ print(res.result.phase)
#~ print(res.phase)
#~ print(res.result)

plt.imshow(res.phase, interpolation='none')
plt.show()
