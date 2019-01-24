# -*- coding: utf-8 -*-

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import sys
import logging

__all__ = ['LOGGER', 'DEFAULT_HANDLER']

LOGGER = logging.getLogger('phasemap')
LOGGER.setLevel(logging.INFO)

DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(DEFAULT_HANDLER)
