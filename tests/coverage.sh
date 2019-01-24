#!/bin/bash
# -*- coding: utf-8 -*-

# © 2015-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

pytest -p no:cov-exclude --cov=phasemap --cov-report=html
