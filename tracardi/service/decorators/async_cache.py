from contextlib import asynccontextmanager

import asyncio
import time
from typing import Callable
from functools import wraps
from collections import deque, defaultdict

from tracardi.context import get_context
from tracardi.exceptions.log_handler import get_logger

locks = defaultdict(asyncio.Lock)
logger = get_logger(__name__)


@asynccontextmanager
async def _lock_for_loading(key):
    # Acquire the lock for the specific key
    async with locks[key]:
        yield


class AsyncCache:
    def __init__(self, ttl: float,
                 max_one_cache_fill_every: float = 0,
                 max_one_func_call_every: float = 0,
                 key_func: Callable = None,
                 allow_null_values: bool = True,
                 use_context: bool = True,
                 lock: bool = True,
                 return_cache_on_error: bool = False,
                 timeout: float = 0):

        self.return_cache_on_error = return_cache_on_error
        self.timeout = timeout
        self.allow_null_values = allow_null_values  # NUll values can be cached
        self.use_context = use_context
        self.lock_for_cache_loading = lock
        self.ttl = ttl
        self.throttle = max_one_cache_fill_every  # max calls per second
        self.key_func = key_func
        self.cache = {}
        self.call_queues = {}

    async def _run(self, key, func: Callable, args, kwargs):
        t = time.time()
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.warning(
                f"ERROR: CACHE FILL: Function `{func.__qualname__}` took {time.time() - t:.3f}. Detail: {str(e)}. Previous cache returned.")
            if not self.return_cache_on_error or not self._is_result_cached(key):
                raise e
            # Else return from cache

            # Make cache longer. Mark it as it was filled.

            self.cache[key]["time"] = time.time()
            return self.cache[key]["result"]

    async def _run_function(self, key, func: Callable, args, kwargs, timeout: float = None):

        t = time.time()
        if self.timeout:
            try:
                result = await asyncio.wait_for(
                    self._run(key, func, args, kwargs),
                    timeout=timeout if timeout is not None else self.timeout  # Timeout in seconds
                )
            except asyncio.exceptions.TimeoutError as e:
                logger.warning(
                    f"TIMEOUT for cache {func.__qualname__} in {time.time() - t:.4f}")
                # If no data raise error
                if not self._is_result_cached(key):
                    raise e
                # Else return from cache
                result = self.cache[key]["result"]
        else:
            result = await self._run(key, func, args, kwargs)

        logger.warning(
            f"Filling for cache {func.__qualname__}{key}. Filled in {time.time() - t:.4f}.")

        return result

    async def _run_and_fill_cache(self, key, func, args, kwargs, timeout: float = None):

        # Execute the function and cache the result
        result = await self._run_function(key, func, args, kwargs, timeout)

        if result is None and not self.allow_null_values:
            return result

        self.cache[key] = {"result": result, "time": time.time()}
        self.update_call_queue(func)
        return result

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = self._generate_key(func, args, kwargs)

            # Check if the result is cached and not expired or if the function is throttled
            if self.is_result_cached_and_valid(key):
                return self.cache[key]["result"]

            if not self.lock_for_cache_loading:
                return await self._run_and_fill_cache(key, func, args, kwargs)

            # Lock
            async with _lock_for_loading(key):

                # AGAIN: Check if the result is cached and not expired or if the function is throttled
                # It may be filled when the execution was stopped by lock.
                if self.is_result_cached_and_valid(key):
                    return self.cache[key]["result"]
                if self.is_function_throttled(func):
                    try:
                        return self.cache[key]["result"]
                    except KeyError:
                        # Fallback, make timeout longer
                        return await self._run_and_fill_cache(key, func, args, kwargs, timeout=10)

                return await self._run_and_fill_cache(key, func, args, kwargs)

        return wrapper

    def _generate_key(self, func: Callable, args, kwargs):
        if self.key_func is not None:
            key = self.key_func(*args, **kwargs)
        else:
            key = f"{func.__qualname__}{args}{tuple(kwargs.items())}"

        if self.use_context:
            context = get_context()
            key = f"{context.__hash__()}:{key}"

        return key

    def _is_result_cached(self, key) -> bool:
        return key in self.cache

    def is_result_cached_and_valid(self, key: str) -> bool:
        return self.ttl > 0 and key in self.cache and time.time() - self.cache[key]["time"] < self.ttl

    def is_function_throttled(self, func: Callable) -> bool:

        if self.throttle <= 0:
            return False

        if func not in self.call_queues:
            self.call_queues[func] = deque()

        call_queue = self.call_queues[func]

        while call_queue and time.time() - call_queue[0] > self.throttle:
            call_queue.popleft()

        if len(call_queue) >= self.throttle:
            return True

        call_queue.append(time.time())
        return False

    def update_call_queue(self, func: Callable):
        if func not in self.call_queues:
            self.call_queues[func] = deque()
        self.call_queues[func].append(time.time())
