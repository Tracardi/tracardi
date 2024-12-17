import time
from collections import defaultdict
from typing import Callable, Any, Awaitable


class Throttler:
    cached_results = defaultdict(dict)

    def __init__(self, resource: str, max_wait_between_calls: float, max_no_execution: float,
                 return_cache_when_throttled: bool = True):
        # How long to wait between allowed function calls. This will give req/s
        # if max_wait_between_calls=0.1 then max req/s is 10 req/s (waits 10% of a second)
        self._max_wait_between_calls = max_wait_between_calls
        self._max_no_execution = max_no_execution
        self._return_cache_when_throttled = return_cache_when_throttled
        self._resource = resource
        self._last_run_time = 0
        self._last_time_func_call = {}

    async def _run(self, key, current_time, func, args, kwargs):
        try:
            result = await func(*args, **kwargs)
            self.cached_results[key] = result
            return result
        finally:
            self._last_run_time = current_time
            self._last_time_func_call[key] = current_time

    def _not_cached(self, key):
        return key not in Throttler.cached_results

    def _get_last_func_run_time(self, key, current_time) -> float:
        return current_time - self._last_time_func_call.get(key, 0)

    def _get_last_throttle_run_time(self, current_time) -> float:
        return current_time - self._last_run_time

    def _is_throttled(self, current_time):
        """
        Throttle means I can call function because I am allowed to.
        """
        return self._get_last_throttle_run_time(current_time) <= self._max_wait_between_calls

    def _is_overdue(self, key, current_time):
        """
        Overdue means I must call function because it waited too long.
        """
        return self._get_last_func_run_time(key, current_time) >= self._max_no_execution

    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:

        # Create a unique key based on function arguments
        key = (f"{func.__module__}.{func.__name__}", args, frozenset(kwargs.items()))
        current_time = time.time()

        # Check if the function can be executed
        if self._not_cached(key) or self._is_overdue(key, current_time) or not self._is_throttled(current_time):
            return await self._run(key, current_time, func, args, kwargs)

        # Throttled
        if not self._return_cache_when_throttled:
            return None

        return Throttler.cached_results.get(key, None)
