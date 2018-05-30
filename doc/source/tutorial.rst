.. _phasemap_tutorial:

Tutorial
========
This tutorial will take you through all the basic steps of using PhaseMap. Since PhaseMap is a **Python library**, you might need some knowledge of Python along the way. If you've never used Python before, you might want to check out the excellent `Python Tutorial <https://docs.python.org/3/tutorial/index.html>`_ first.

Basic usage
-----------


.. ipython::

    In [0]: def phase(pos):
       ...:     x, y = pos
       ...:     return int(x**2 + y**2 < 1)

.. ipython::

    In [0]: import phasemap as pm

    In [0]: res = pm.run(
       ...:     phase,
       ...:     limits=[(-1, 1), (-1, 1)],
       ...:     mesh=3,
       ...: )

    In [0]: print('Points:', res.points)
       ...: print('Boxes:', res.boxes)
       ...: print('Limits:', res.limits)

.. ipython::

    In [0]: res2 = pm.run(
       ...:     phase,
       ...:     limits=[(-1, 1), (-1, 1)],
       ...:     mesh=3,
       ...:     num_steps=8
       ...: )


Plotting
--------

For two-dimensional problems, PhaseMap includes helper functions to create plots. These functions are based on matplotlib, meaning that the usual functions used in matplotlib to customize plots are available.

To create a plot that shows the boxes in the result, use the :func:`phasemap.plot.boxes` function. Each box is colored according to the phase of the points it contains. If there are multiple phases within the box, it is considered undecided and colored in white.

.. ipython::

    In [0]: import matplotlib.pyplot as plt
       ...: from matplotlib.colors import ListedColormap
       ...: plt.register_cmap('custom_cmap', ListedColormap(['#003399', '#EE6600'], name='custom_cmap'))
       ...: plt.set_cmap('custom_cmap')

    In [0]: pm.plot.boxes(res)

    In [0]: plt.savefig('source/_static/tutorial_plot_boxes.png', bbox_inches='tight')

This produces the following image:

.. image:: _static/tutorial_plot_boxes.png

Alternatively, you can plot the points where the function was evaluated with :func:`phasemap.plot.points`:

.. ipython::

    In [0]: pm.plot.points(res, s=2.)

    In [0]: plt.savefig('source/_static/tutorial_plot_points.png', bbox_inches='tight')

.. image:: _static/tutorial_plot_points.png

Plotting the result of the calculation with a higher ``num_steps`` produces the following image:

.. ipython::

    In [0]: pm.plot.boxes(res2)

    In [0]: plt.savefig('source/_static/tutorial_plot_boxes2.png', bbox_inches='tight')

.. image:: _static/tutorial_plot_boxes2.png

Saving Results
--------------

TODO

Improving Performance
---------------------

The implementation of PhaseMap is based on Python's coroutine functionality. This can be leveraged to improve the performance, especially when evaluating a single point takes a lot of time. Consider the following code, where we artificially increased the runtime of the ``phase_slow`` function:

.. ipython::

    In [0]: import time
       ...: import asyncio

    In [0]: def phase_slow(pos):
       ...:     time.sleep(0.1)
       ...:     return phase(pos)

    In [0]: %timeit pm.run(phase_slow, limits=[(0, 1), (0, 1)], mesh=3, num_steps=1)

The calls to ``phase_slow`` happen sequentially, which means that the runtime increases very quickly with the number of evaluations that are done. If the code which evaluates the phase is also coroutine-based, this can be improved easily by passing a coroutine instead of a regular function to :func:`phasemap.run`:

.. ipython::

    In [0]: async def async_phase_slow(pos):
       ...:     await asyncio.sleep(0.1)
       ...:     return phase(pos)

    In [0]: %timeit pm.run(async_phase_slow, limits=[(0, 1), (0, 1)], mesh=3, num_steps=1)

However, in most cases this would require substantial changes in the function that evaluates the phase. Instead, you can also use a :py:class:`ThreadPoolExecutor <concurrent.futures.ThreadPoolExecutor>` or :py:class:`ProcessPoolExecutor <concurrent.futures.ProcessPoolExecutor>` to run the function in parallel on multiple threads / processes. To use this with PhaseMap, you need to wrap the function in a coroutine which submits it to the executor:

.. ipython::

    In [0]: from concurrent.futures import ThreadPoolExecutor
       ...: executor = ThreadPoolExecutor(max_workers=1000)
       ...: event_loop = asyncio.get_event_loop()

    In [0]: async def pool_phase_slow(pos):
       ...:     return await event_loop.run_in_executor(executor, phase_slow, pos)

    In [0]: %timeit pm.run(pool_phase_slow, limits=[(0, 1), (0, 1)], mesh=3, num_steps=1)

This approach can dramatically reduce the run-time needed to calculate a phase diagram with PhaseMap. It is especially suited to cases where so-called "serial farming" can be used, meaning that many concurrent processes (e.g. on a cluster) each calculate the phase at a specific point.
