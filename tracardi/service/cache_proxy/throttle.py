import time
from collections import defaultdict
from typing import Callable, Any, Awaitable


class Throttler:

    cached_results = defaultdict(dict)
    last_run_time = {}

    def __init__(self, interval: float):
        """
        Initialize the throttler with a specific interval.
        :param interval: Minimum time (in seconds) between consecutive executions.
        """
        self.interval = interval

    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Call the provided function with throttling.
        :param func: Function to be throttled.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: Cached or newly computed result of the function.
        """
        # Create a unique key based on function arguments
        key = (func, args, frozenset(kwargs.items()))
        current_time = time.time()

        # Check if the function can be executed
        if key not in self.last_run_time or current_time - self.last_run_time[key] >= self.interval:
            # Run the function and store the result
            result = await func(*args, **kwargs)
            Throttler.cached_results[key] = result
            Throttler.last_run_time[key] = current_time
        else:
            result = Throttler.cached_results[key]

        return result

