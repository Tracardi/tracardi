from contextlib import contextmanager

from tracardi.service.adapter.cache.cache_protocol import CacheProtocol


@contextmanager
def distributed_lock(redis_adapter: CacheProtocol, key: str, expires: int):

    # Generate a unique lock identifier and incorporate it into the key name
    lock_key = f"lock:{key}"

    # Attempt to acquire the lock by setting the key if it doesn't already exist
    is_locked = redis_adapter.set(lock_key, "", nx=True, ex=expires)

    if is_locked:
        try:
            yield True
        finally:
            # If we hold the lock, just delete the exact key we created
            redis_adapter.delete(lock_key)
    else:
        # Could not acquire the lock. It already exists and will be released by other process or expires
        yield False
