import asyncio
from collections.abc import Awaitable

NOT_FOUND = object()


class FuncCache:
    """
    Caches calls to a function or coroutine.
    """

    def __init__(self, func, data=None):
        self.func = _wrap_to_coroutine(func)
        self.data = data if data is not None else dict()
        self.needs_saving = False
        self.awaitables = dict()

    async def __call__(self, inp):
        if inp in self.data:
            return self.data[inp]

        if inp in self.awaitables:
            result = await asyncio.wait_for(self.awaitables[inp], timeout=None)
        else:
            fut = asyncio.ensure_future(self.func(inp))
            self.awaitables[inp] = fut
            result = await fut
            self.awaitables.pop(inp)
        self.data[inp] = result
        self.needs_saving = True
        return result


def _wrap_to_coroutine(func):
    async def inner(inp):
        res = func(inp)
        if isinstance(res, Awaitable):
            res = await res
        return res

    return inner
