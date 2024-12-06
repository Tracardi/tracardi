from typing import Optional, Any
from tracardi.service.adapter.cache_adaper_selector import cache_adapter

_cache = cache_adapter()

def _delete_cache(key: str, collection: str):
    _cache.delete(f"{collection}{key}")


def _has_cache(key: str, key_namespace: str):
    return _cache.exists(f"{key_namespace}{key}")


def _get_cache(key: str, collection: str) -> Optional[Any]:
    return _cache.get_msgpack(f"{collection}{key}")



def _set_cache(key: str, value: Any, collection: str, ttl):
    _cache.set_msgpack(
        f"{collection}{key}",
        value,
        ex=ttl
    )


def _ttl(key: str, collection: str):
    return _cache.ttl(f"{collection}{key}")
