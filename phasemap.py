#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    25.08.2016 14:58:52 CEST
# File:    phasemap.py

import numpy as np
from collections import namedtuple

PhaseResult = namedtuple('PhaseResult', ['phase', 'virtual'])
