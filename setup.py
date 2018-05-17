import re
from setuptools import setup

README = r"""The PhaseMap algorithm maps a phase diagram, given a function to evaluate the phase at a given point. The number of phase evaluations needed scales with the dimension of the phase boundary, instead of the dimenstion of the phase space. Thus, this algorithm is efficient when evaluating the phase is relatively expensive.
"""

with open('./phasemap/__init__.py', 'r') as f:
    MATCH_EXPR = "__version__[^'\"]+(['\"])([^'\"]+)"
    VERSION = re.search(MATCH_EXPR, f.read()).group(2).strip()

setup(
    name='phasemap',
    version=VERSION,
    url='http://z2pack.ethz.ch/phasemap',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    description='Algorithm for mapping phase diagrams',
    install_requires=[
        'numpy', 'matplotlib', 'msgpack-python', 'decorator', 'fsc.export',
        'fsc.iohelper'
    ],
    extras_require={'dev': ['yapf==0.21', 'pre-commit', 'pytest', 'pylint']},
    long_description=README,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English', 'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Development Status :: 4 - Beta'
    ],
    license='GPL',
    keywords=['phase', 'map', 'diagram', 'scaling'],
    packages=['phasemap', 'phasemap.io']
)
