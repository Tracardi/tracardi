from typing import Tuple

from tracardi.service.adapter.cache_adaper_selector import cache_adapter
from tracardi.service.storage.redis.collections import Collection


_cache = cache_adapter()

class Limiter:

    def __init__(self, limit: int, ttl: int):
        self._ttl = ttl
        self._limit = limit

    def limit(self, key: str) -> Tuple[bool, int]:

        key = f"{Collection.throttle}:{key}"

        req = _cache.incr(key)
        if req == 1:
            _cache.expire(key, self._ttl)
            ttl = self._ttl
        else:
            ttl = _cache.ttl(key)

        return req <= self._limit, ttl
