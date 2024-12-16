import time
from collections import defaultdict
from typing import Callable, Any, Awaitable

class Throttler:

    cached_results = defaultdict(dict)

    def __init__(self, resource: str, interval: float, return_cache_when_throttled:bool=True):
        self._return_cache_when_throttled = return_cache_when_throttled
        self._resource = resource
        self.interval = interval
        self._last_run_time = 0

    async def _run(self, key, current_time, func, args, kwargs):
        result = await func(*args, **kwargs)
        Throttler.cached_results[key] = result
        self._last_run_time = current_time
        return result

    def not_cached(self, key):
        return key not in Throttler.cached_results

    def is_throttled(self, current_time):
        return current_time - self._last_run_time <= self.interval

    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:

        # Create a unique key based on function arguments
        key = (func, args, frozenset(kwargs.items()))
        current_time = time.time()

        # Check if the function can be executed
        if not self.is_throttled(current_time) or self.not_cached(key):
            return await self._run(key, current_time, func, args, kwargs)

        # Throttled
        if not self._return_cache_when_throttled:
            return None

        return Throttler.cached_results.get(key, None)

