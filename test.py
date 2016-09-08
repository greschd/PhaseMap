#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.08.2016 04:11:07 CEST
# File:    test.py

from phasemap import *

A = PhaseMap([2, 2], [(0, 1), (0, 2)])

for idx in A.indices():
    A[idx] = 2 * idx[0] + idx[1]
    
print(A.data)
A.extend()
print(A.data)

print(A.index_to_position([2, 2]))
