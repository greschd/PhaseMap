import re
import sys
from setuptools import setup

if sys.version_info < (3, 5):
    raise 'Must use Python version 3.5 or higher.'

README = r"""The PhaseMap algorithm maps a phase diagram, given a function to evaluate the phase at a given point. The number of phase evaluations needed scales with the dimension of the phase boundary, instead of the dimenstion of the phase space. Thus, this algorithm is efficient when evaluating the phase is relatively expensive.
"""

with open('./phasemap/__init__.py', 'r') as f:
    MATCH_EXPR = "__version__[^'\"]+(['\"])([^'\"]+)"
    VERSION = re.search(MATCH_EXPR, f.read()).group(2).strip()

EXTRAS_REQUIRE = dict(
    dev=[
        'yapf==0.24', 'pre-commit==1.8.2', 'pylint==2.1.1', 'prospector==1.1.2'
    ],
    test=['msgpack', 'pytest', 'pytest-cov'],
    doc=['sphinx', 'sphinx-rtd-theme', 'ipython']
)
EXTRAS_REQUIRE['dev'] += EXTRAS_REQUIRE['test'] + EXTRAS_REQUIRE['doc']

setup(
    name='phasemap',
    version=VERSION,
    url='http://z2pack.ethz.ch/phasemap',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    description='Algorithm for calculating phase diagrams',
    install_requires=[
        'numpy', 'matplotlib', 'decorator', 'fsc.export',
        'fsc.iohelper>=1.0.2', 'fsc.async-tools'
    ],
    extras_require=EXTRAS_REQUIRE,
    long_description=README,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English', 'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Development Status :: 5 - Production/Stable'
    ],
    license='Apache 2.0',
    keywords=['phase', 'map', 'diagram', 'scaling'],
    packages=['phasemap', 'phasemap.io']
)
