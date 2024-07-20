import asyncio
from typing import Dict, Tuple, Any, Callable

import functools

from tracardi.context import get_context
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem

cache: Dict[str, MemoryCache] = {}


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


def _run_function(func, args, kwargs, max_size, allow_null_values, key_func: Callable = None,
                  use_context: bool = True) -> Tuple[Any, str, str]:
    # Construct a unique cache key from the function's module name,
    # function name, args, and kwargs to avoid collisions.

    func_key = _func_key(func, use_context)

    if key_func is not None:
        args_key = key_func(*args, **kwargs)
    else:
        args_key = _args_key(args, kwargs)

    # Create cache
    if func_key not in cache:
        cache[func_key] = MemoryCache(
            func_key,
            max_pool=max_size,
            allow_null_values=allow_null_values,
            use_context=False  # It is already with context key
        )

    # Check cache
    if args_key in cache[func_key]:
        return cache[func_key][args_key].data, func_key, args_key

    result = func(*args, **kwargs)

    return result, func_key, args_key


def async_cache_for(ttl, max_size=1000, allow_null_values=False, key_func: Callable = None, use_context: bool = True):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result, func_key, args_key = _run_function(func, args, kwargs, max_size, allow_null_values, key_func,
                                                       use_context)
            if asyncio.iscoroutine(result):
                result = await result

            # Update cache
            cache[func_key][args_key] = CacheItem(data=result, ttl=ttl)
            return result

        return async_wrapper

    return decorator


def cache_for(ttl, max_size=1000, allow_null_values=False, key_func: Callable = None, use_context: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            result, func_key, args_key = _run_function(func, args, kwargs, max_size, allow_null_values, key_func,
                                                       use_context)

            # Update cache
            cache[func_key][args_key] = CacheItem(data=result, ttl=ttl)
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
