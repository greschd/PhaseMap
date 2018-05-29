from collections.abc import Awaitable

NOT_FOUND = object()


class FuncCache:
    """
    Caches calls to a function or coroutine.
    """

    def __init__(self, func, data=None):
        self.func = _wrap_to_coroutine(func)
        self.data = data if data is not None else dict()
        self.awaitables = dict()

    async def __call__(self, inp):
        if inp in self.data:
            return self.data[inp]

        if inp in self.awaitables:
            result = await self.awaitables[inp]
        else:
            coro = self.func(inp)
            self.awaitables[inp] = coro
            result = await coro
        self.data[inp] = result
        return result


def _wrap_to_coroutine(func):
    async def inner(inp):
        res = func(inp)
        if isinstance(res, Awaitable):
            res = await res
        return res

    return inner
