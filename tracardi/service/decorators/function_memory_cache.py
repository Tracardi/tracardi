import asyncio
import inspect
from collections import defaultdict

from time import time
from typing import Dict, Tuple, Any, Callable

import functools

from tracardi.context import get_context
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from contextlib import asynccontextmanager

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.time_converters import pretty_time_format

# Cache DB
cache: Dict[str, MemoryCache] = {}

# Dictionary to store locks for each key
locks = defaultdict(asyncio.Lock)
logger = get_logger(__name__)


@asynccontextmanager
async def _lock_for_loading(key, params):
    # Acquire the lock for the specific key
    async with locks[key]:
        yield


def _args_key(args, kwargs):
    key_parts = [args]
    key_parts.extend(f'{k}={v}' for k, v in kwargs.items())
    return ':'.join(map(str, key_parts))


def _func_key(func, use_context: bool = True):
    if use_context:
        context = get_context()
        key_parts = [context.__hash__(), func.__module__, func.__qualname__]
    else:
        key_parts = [func.__module__, func.__qualname__]

    return ':'.join(map(str, key_parts))


def _func_params_key(key_func, args, kwargs):
    if key_func is not None:
        args_key = key_func(*args, **kwargs)
    else:
        args_key = _args_key(args, kwargs)

    return args_key


def _init_funct_cache(func_key, max_size, allow_null_values):
    if func_key not in cache:
        cache[func_key] = MemoryCache(
            func_key,
            max_pool=max_size,
            allow_null_values=allow_null_values,
            use_context=False  # It is already with context key
        )
    return cache


def _run_function(ttl: float, func, args, kwargs, max_size, allow_null_values, key_func: Callable = None,
                  use_context: bool = True) -> Tuple[Any, str, str]:
    # Construct a unique cache key from the function's module name,
    # function name, args, and kwargs to avoid collisions.

    global cache

    func_key = _func_key(func, use_context)
    args_key = _func_params_key(key_func, args, kwargs)

    # Create cache
    cache = _init_funct_cache(func_key, max_size, allow_null_values)

    # Check cache
    if args_key in cache[func_key]:
        return cache[func_key][args_key].data, func_key, args_key

        # Check lock is it is not already loading data.

    result = func(*args, **kwargs)

    # Update cache
    cache[func_key][args_key] = CacheItem(data=result, ttl=ttl)

    return result, func_key, args_key


async def _async_exec(ttl, func, func_key, timeout: float, args_key, args, kwargs):
    # Check cache again it may be filled already

    if args_key in cache[func_key]:
        # 2nd attempt to check cache.When being locked the cache could have been filled.
        return cache[func_key][args_key].data, func_key, args_key

    # Check lock is it is not already loading data.
    t = time()

    if timeout:
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=timeout  # Timeout in seconds
            )
        except asyncio.exceptions.TimeoutError as e:
            logger.warning(
                f"TIMEOUT for cache {func_key}{args_key}: ttl: {pretty_time_format(ttl)}s: [Timeout in: {time() - t:.3f}]")
            # If no data raise error
            _expired = cache[func_key].get_expired(args_key)
            if _expired is None:
                raise e
            # Else return from cache
            return _expired.data, func_key, args_key
    else:
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result

    logger.warning(f"Filling cache {func_key}{args_key}: ttl: {pretty_time_format(ttl)}s: [Filled in: {time() - t:.3f}]")
    # Update cache
    cache[func_key][args_key] = CacheItem(data=result, ttl=ttl)

    return result, func_key, args_key


async def _run_async_function(
        ttl: float, func, args, kwargs, max_size, allow_null_values,
        locked: bool,
        key_func: Callable = None,
        use_context: bool = True,
        timeout: float = None

) -> Tuple[Any, str, str]:
    # Construct a unique cache key from the function's module name,
    # function name, args, and kwargs to avoid collisions.

    global cache

    func_key = _func_key(func, use_context)
    args_key = _func_params_key(key_func, args, kwargs)

    # Create cache
    cache = _init_funct_cache(func_key, max_size, allow_null_values)
    if args_key in cache[func_key]:
        # First attempt to check cache. It may be in memory already
        return cache[func_key][args_key].data, func_key, args_key

    if locked:
        async with _lock_for_loading(func_key, args_key):
            return await _async_exec(ttl, func, func_key, timeout, args_key, args, kwargs)

    return await _async_exec(ttl, func, func_key, timeout, args_key, args, kwargs)


def async_cache_for(ttl: float, max_size=1000, allow_null_values=False, key_func: Callable = None,
                    use_context: bool = True, lock: bool = True, timeout: float = 0):
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"Incorrect cache type for async function {func.__module__}.{func.__qualname__}. "
                            f"Expected `cache_for`, got `async_cache_for` for not async function. "
                            f"Use `cache_for`.")

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result, func_key, args_key = await _run_async_function(
                ttl,
                func, args, kwargs,
                max_size, allow_null_values,
                lock,
                key_func,
                use_context,
                timeout
            )

            return result

        return async_wrapper

    return decorator


def cache_for(ttl, max_size=1000, allow_null_values=False, key_func: Callable = None, use_context: bool = True):
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            raise TypeError(f"Incorrect cache type for function {func.__module__}.{func.__qualname__}. "
                            f"Expected `async_cache_for`, got `cache_for` for not async function.  "
                            f"Use `async_cache_for`.")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            result, func_key, args_key = _run_function(
                ttl,
                func, args, kwargs,
                max_size, allow_null_values, key_func,
                use_context)

            return result

        return sync_wrapper

    return decorator


def delete_cache(func, *args, **kwargs):
    args_key = _args_key(args, kwargs)
    func_key = _func_key(func, True)
    try:
        cache_item = cache[func_key]
        cache_item.delete(args_key)
    except KeyError:
        pass


def has_cache(func, *args, **kwargs) -> bool:
    args_key = _args_key(args, kwargs)
    func_key = _func_key(func, True)
    if func_key not in cache:
        return False
    cache_item = cache[func_key]
    return args_key in cache_item
