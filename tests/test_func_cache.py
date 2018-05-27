import asyncio

import pytest

from phasemap._cache import FuncCache


def echo(x):
    return x


async def echo_async(x):
    return x


def error(x):
    raise ValueError(x)


@pytest.mark.parametrize('func', [echo, echo_async])
def test_func_cache(func):
    async def run():
        func_cache = FuncCache(func)
        for x in range(10):
            assert x == await func_cache(x)
        func_error = FuncCache(error, data=func_cache.data)
        for x in range(10):
            assert x == await func_error(x)
        with pytest.raises(ValueError):
            await func_error(10)

    asyncio.get_event_loop().run_until_complete(run())
