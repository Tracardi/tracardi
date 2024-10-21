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
                 max_one_call_every: float,
                 key_func: Callable = None,
                 allow_null_values: bool = False,
                 use_context: bool = True,
                 lock: bool = True,
                 timeout: float = 0):

        self.timeout = timeout
        self.allow_null_values = allow_null_values  # NUll values can be cached
        self.use_context = use_context
        self.lock = lock
        self.ttl = ttl
        self.throttle = max_one_call_every  # max calls per second
        self.key_func = key_func
        self.cache = {}
        self.call_queues = {}

    async def _run_function(self, key, func, args, kwargs):
        logger.warning(
            f"Filling for cache {func.__qualname__}({key})")
        if self.timeout:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.timeout  # Timeout in seconds
                )
            except asyncio.exceptions.TimeoutError as e:
                logger.warning(
                    f"TIMEOUT for cache {func.__qualname__}")
                # If no data raise error
                if not self._is_result_cached(key):
                    raise e
                # Else return from cache
                return self.cache[key]["result"]
        else:
            return await func(*args, **kwargs)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = self.generate_key(func, args, kwargs)

            # Check if the result is cached and not expired
            if self.ttl > 0 and self.is_result_cached_and_valid(key):
                print('cache')
                return self.cache[key]["result"]

            # Check if the function is throttled
            if self.throttle > 0 and self.is_function_throttled(func):
                print('throttle')
                return self.cache[key]["result"]

            # Execute the function and cache the result
            if self.lock:
                # Lock
                async with _lock_for_loading(key):
                    result = await self._run_function(key, func, args, kwargs)
            else:
                result = await self._run_function(key, func, args, kwargs)

            if result is None and not self.allow_null_values:
                return result

            self.cache[key] = {"result": result, "time": time.time()}
            self.update_call_queue(func)
            return result

        return wrapper

    def generate_key(self, func: Callable, args, kwargs):
        if self.key_func:
            key = self.key_func(args, kwargs)
        else:
            key = f"{func.__qualname__}{hash(args)}{hash(tuple(kwargs.items()))}"

        if self.use_context:
            context = get_context()
            return f"{context.__hash__()}:{key}"

        return key

    def _is_result_cached(self, key) -> bool:
        return key in self.cache

    def is_result_cached_and_valid(self, key: str) -> bool:
        return key in self.cache and time.time() - self.cache[key]["time"] < self.ttl

    def is_function_throttled(self, func: Callable) -> bool:
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
