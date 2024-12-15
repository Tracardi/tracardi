import time
from collections import defaultdict
from typing import Callable, Any, Awaitable


class Throttler:

    cached_results = defaultdict(dict)
    last_run_time = {}

    def __init__(self, resource: str, interval: float):
        self._resource = resource
        self.interval = interval

    def is_throttled(self, current_time):
        return self._resource in Throttler.last_run_time and current_time - Throttler.last_run_time[self._resource] <= self.interval

    async def call(self, namespace:str, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:

        # Create a unique key based on function arguments
        key = (func, args, frozenset(kwargs.items()))
        current_time = time.time()
        # Check if the function can be executed
        if self.is_throttled(current_time):
            result = Throttler.cached_results[key]
        else:
            # Run the function and store the result
            result = await func(*args, **kwargs)
            Throttler.cached_results[key] = result
            Throttler.last_run_time[self._resource] = current_time

        return result

