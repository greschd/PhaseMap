import json
import asyncio
import tempfile
from collections import Counter

import pytest
import phasemap as pm

from phases import phase1, phase2, phase3


@pytest.mark.parametrize('num_steps', [0, 1, 3])
@pytest.mark.parametrize(
    'phase, limits', [(phase1, [(-1, 1), (-1, 1)]), (phase2, [(0, 1), (0, 1)])]
)
def test_phase(compare_result_equal, num_steps, phase, limits):
    res = pm.run(
        phase,
        limits,
        num_steps=num_steps,
        mesh=3,
    )

    compare_result_equal(res)


def test_save_file(results_equal):
    with tempfile.NamedTemporaryFile() as tmpf:
        res = pm.run(
            phase1, limits=[(-1, 1)] * 2, num_steps=2, save_file=tmpf.name
        )
        assert results_equal(res, pm.io.load(tmpf.name, serializer=json))


def test_init_result(results_equal):
    def error(x):  # pylint: disable=unused-argument
        raise ValueError

    res1 = pm.run(phase1, limits=[(-1, 1)] * 2, num_steps=2)
    res2 = pm.run(error, limits=[(-1, 1)] * 2, num_steps=2, init_result=res1)
    results_equal(res1, res2)


def test_load(results_equal):
    def error(x):  # pylint: disable=unused-argument
        raise ValueError

    with tempfile.NamedTemporaryFile() as tmpf:
        res1 = pm.run(
            phase1, limits=[(-1, 1)] * 2, num_steps=2, save_file=tmpf.name
        )
        res2 = pm.run(
            error,
            limits=[(-1, 1)] * 2,
            num_steps=2,
            save_file=tmpf.name,
            load=True,
            serializer=json
        )
        results_equal(res1, res2)


def test_load_invalid():
    with pytest.raises(IOError):
        pm.run(
            phase1,
            limits=[(-1, 1)] * 2,
            num_steps=2,
            save_file='inexistent_file',
            load=True,
            load_quiet=False,
            serializer=json
        )


def test_load_init_result_conflict():
    res1 = pm.run(phase1, limits=[(-1, 1)] * 2, num_steps=2)
    with tempfile.NamedTemporaryFile() as tmpf:
        with pytest.raises(ValueError):
            pm.run(
                phase1,
                limits=[(-1, 1)] * 2,
                num_steps=2,
                save_file=tmpf.name,
                load=True,
                init_result=res1
            )


def test_complex_phase(compare_result_equal):
    res = pm.run(
        phase3,
        [(0, 1), (0, 1)],
        num_steps=8,
        mesh=2,
    )

    compare_result_equal(res)


@pytest.mark.parametrize(
    'phase, limits', [(phase1, [(-1, 1), (-1, 1), (-1, 1)])]
)
def test_3d(compare_result_equal, phase, limits):
    res = pm.run(
        phase,
        limits=limits,
        num_steps=1,
        mesh=3,
    )
    compare_result_equal(res)


@pytest.mark.parametrize('mesh', [2, 4])
@pytest.mark.parametrize('num_steps_1', [0, 2])
@pytest.mark.parametrize('num_steps_2', [0, 1])
@pytest.mark.parametrize('save', [True, False])
def test_restart(results_equal, mesh, num_steps_1, num_steps_2, save):
    num_steps_total = num_steps_1 + num_steps_2
    res = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps_total,
        mesh=mesh,
    )

    res2 = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps_1,
        mesh=mesh,
    )
    if save:
        with tempfile.NamedTemporaryFile() as tmpf:
            pm.io.save(res2, tmpf.name, serializer=json)
            res2 = pm.io.load(tmpf.name, serializer=json)
    res3 = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps_total,
        init_result=res2,
        mesh=mesh,
    )
    results_equal(res, res3)


@pytest.mark.parametrize('num_steps', range(3))
def test_restart_nocalc(results_equal, num_steps):
    def error(x):
        raise ValueError(x)

    res = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps,
        mesh=3,
    )

    res_restart = pm.run(
        error,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps,
        mesh=3,
        init_result=res,
    )
    results_equal(res, res_restart)


@pytest.mark.parametrize('mesh', [1, (2, 2), (3, 2, 1)])
def test_invalid_mesh(mesh):
    with pytest.raises(ValueError):
        pm.run(phase1, limits=[(0, 1), (0, 1), (0, 1)], mesh=mesh)


def test_caching():
    def _call_count(func):
        count = Counter()

        async def inner(inp):
            count.update([inp])
            await asyncio.sleep(0.)
            return func(inp)

        return inner, count

    func, count = _call_count(phase3)
    pm.run(
        func,
        [(0, 1), (0, 1)],
        num_steps=5,
        mesh=2,
    )
    assert all(val <= 1 for val in count.values())


def test_raises():
    def func(val):  # pylint: disable=unused-argument
        raise ValueError('test succeeded.')

    with pytest.raises(ValueError):
        pm.run(func, limits=[(0, 1)])
