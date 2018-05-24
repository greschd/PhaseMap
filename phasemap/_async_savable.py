import abc
import asyncio
try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager

class AsyncSavable(abc.ABC):
    def __init__(self, save_file, delay=1.):
        self._save_file = save_file
        self._delay = delay
        self._needs_saving = False

    @asynccontextmanager
    async def run_save_loop(self, event_loop):
        save_task = event_loop.create_task(self._save_loop())
        await asyncio.sleep(0.) # Allow the save loop to start.
        yield
        save_task.cancel()
        await save_task

    async def _save_loop(self):
        try:
            if not self._save_file:
                return
            while True:
                await asyncio.sleep(self._delay)
                self._do_save_if_needed()
        except asyncio.CancelledError:
            self._do_save_if_needed()

    def _do_save_if_needed(self):
        if self._needs_saving:
            self._needs_saving = False
            self._do_save()

    @abc.abstractmethod
    def _do_save(self):
        pass
