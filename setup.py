#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.10.2014 11:27:40 CEST
# File:    setup.py

import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = r"""The PhaseMap algorithm maps a phase diagram, given a function to evaluate the phase at a given point. The number of phase evaluations needed scales with the dimension of the phase boundary, instead of the dimenstion of the phase space. Thus, this algorithm is efficient when evaluating the phase is relatively expensive.
"""

with open('./phasemap/_version.py', 'r') as f:
    match_expr = "__version__[^'" + '"]+([' + "'" + r'"])([^\1]+)\1'
    version = re.search(match_expr, f.read()).group(2).strip()

setup(
    name='phasemap',
    version=version,
    url='http://z2pack.ethz.ch/phasemap',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    description='Algorithm for mapping phase diagrams',
    install_requires=['numpy', 'fsc.export'],
    long_description=readme,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Development Status :: 4 - Beta'
    ],
    license='GPL',
    keywords=['phase', 'map', 'diagram', 'scaling'],
    packages=['phasemap', 'phasemap2']
)
