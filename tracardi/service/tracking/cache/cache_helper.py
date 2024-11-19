import msgpack
from typing import Optional, Any
from tracardi.service.adapter.cache.redis.redis_cache_adapter import redis_cache_adapter

_cache = redis_cache_adapter

def _delete_cache(key: str, collection: str):
    _cache.delete(f"{collection}{key}")


def _has_cache(key: str, key_namespace: str):
    return _cache.exists(f"{key_namespace}{key}")


def _get_cache(key: str, collection: str) -> Optional[Any]:
    value = _cache.get(f"{collection}{key}")
    if value is None:
        return None

    return msgpack.unpackb(value)


def _set_cache(key: str, value: Any, collection: str, ttl):
    _cache.set(
        f"{collection}{key}",
        msgpack.packb(value),
        ex=ttl
    )


def _ttl(key: str, collection: str):
    return _cache.ttl(f"{collection}{key}")
