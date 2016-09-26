#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    17.09.2016 13:55:39 CEST
# File:    _logging_setup.py

import sys
import logging

__all__ = ['logger']

logger = logging.getLogger('phasemap')
#~ logger.setLevel(logging.INFO)
#~ DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
#~ logger.addHandler(DEFAULT_HANDLER)
