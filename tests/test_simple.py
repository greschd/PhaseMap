import json
import tempfile

import pytest
import phasemap as pm

from phases import phase1, phase2


@pytest.mark.parametrize('num_steps', [0, 1, 3])
@pytest.mark.parametrize(
    'phase, limits', [(phase1, [(-1, 1), (-1, 1)]), (phase2, [(0, 1), (0, 1)])]
)
def test_phase(
    compare_equal, compare_result_equal, num_steps, phase, limits
):
    res = pm.run(
        phase,
        limits,
        num_steps=num_steps,
        init_mesh=3,
    )

    compare_equal(sorted([(tuple(k), v.phase) for k, v in res.points.items()]))
    compare_result_equal(res, tag='with_encoding')


@pytest.mark.parametrize(
    'phase, limits', [(phase1, [(-1, 1), (-1, 1), (-1, 1)])]
)
def test_3d(compare_equal, compare_result_equal, phase, limits):
    res = pm.run(
        phase,
        limits=limits,
        num_steps=1,
        init_mesh=3,
    )
    compare_equal(sorted([(tuple(k), v.phase) for k, v in res.points.items()]))
    compare_result_equal(res, tag='with_encoding')


@pytest.mark.parametrize('init_mesh', [2, 4])
@pytest.mark.parametrize('num_steps_1', [0, 2])
@pytest.mark.parametrize('num_steps_2', [0, 1])
@pytest.mark.parametrize('save', [True, False])
def test_restart(results_equal, init_mesh, num_steps_1, num_steps_2, save):
    num_steps_total = num_steps_1 + num_steps_2
    res = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps_total,
        init_mesh=init_mesh,
    )

    res2 = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps_1,
        init_mesh=init_mesh,
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
        init_mesh=init_mesh,
    )
    assert sorted([
        (tuple(k), v.phase) for k, v in res.points.items()
    ]) == sorted([(tuple(k), v.phase) for k, v in res3.points.items()])
    results_equal(res, res3)


@pytest.mark.parametrize('num_steps', range(3))
def test_restart_nocalc(results_equal, num_steps):
    def error(x):
        raise ValueError(x)

    res = pm.run(
        phase1,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps,
        init_mesh=3,
    )

    res_restart = pm.run(
        error,
        [(-1, 1), (-1, 1)],
        num_steps=num_steps,
        init_mesh=3,
        init_result=res,
    )
    results_equal(res, res_restart)
