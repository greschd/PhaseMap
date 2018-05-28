from collections.abc import Awaitable

NOT_FOUND = object()


class FuncCache:
    """
    Caches calls to a (possibly async) function.
    """

    def __init__(self, func, data=None):
        self.func = func
        if data is None:
            self.data = dict()
        else:
            self.data = data

    async def __call__(self, inp):
        try:
            return self.data[inp]
        except KeyError:
            result = self.func(inp)
            if isinstance(result, Awaitable):
                result = await result
            self.data[inp] = result
            return result
