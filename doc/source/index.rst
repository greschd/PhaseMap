.. image:: images/logo_on_white.png
    :width: 400px
    :alt: PhaseMap

|

.. title:: Overview

.. container:: section
    
    is a tool for calculating phase diagrams. It uses a quadtree algorithm that tracks the phase boundary. The key advantage of this approach is that it **scales** with the **dimension of the phase boundary** instead of the full phase space. This is especially important when evaluating a single point in the phase space is an expensive operation.

    .. rubric:: Please cite

    * Dominik Gresch, Mario Könz, Donjan Rodic, Alexey A. Soluyanov, Matthias Troyer *"Boundary Search Algorithm for Mapping Phase Diagrams."* [in preparation]

.. rubric:: Parts of the documentation

| :ref:`phasemap_tutorial`
| start here
|
| :ref:`phasemap_reference`
| detailed description of the classes and functions
|

.. rubric:: Getting in touch

The development version of PhaseMap is hosted on `GitHub <http://github.com/Z2PackDev/PhaseMap>`_ . Post an issue there or contact `me <http://github.com/greschd>`_ directly with questions / suggestions / feedback about PhaseMap.

.. rubric:: Indices and tables

| :ref:`genindex`
| list of all functions and classes
|
| :ref:`modindex`
| list of all modules and submodules

.. toctree::
    :maxdepth: 2
    :hidden:
    
    tutorial.rst
    reference.rst
