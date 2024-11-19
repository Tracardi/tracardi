import inspect
import msgpack
from functools import wraps

from tracardi.service.adapter.cache.redis.redis_cache_adapter import redis_cache_adapter
from tracardi.service.storage.redis.collections import Collection

# Connect to Redis
cache = redis_cache_adapter

def redis_cache(key_param):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_param not in kwargs:
                raise ValueError(f"The key parameter '{key_param}' is required")

            # Directly use the key parameter value from kwargs
            key_value = kwargs[key_param]

            # Create a unique key based on the function's name and the key parameter value
            key = f"{Collection.function_cache}:{func.__name__}:{str(key_value)}"

            # Try to get the cached value from Redis
            cached_value = cache.get(key)

            if cached_value is not None:
                return msgpack.loads(cached_value, raw=False)

            # Call the function and cache its result
            result = func(*args, **kwargs)
            if inspect.iscoroutine(result):
                result = await result

            cache.set(key, msgpack.dumps(result))
            return result

        return wrapper
    return decorator
