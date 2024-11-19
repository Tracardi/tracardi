from typing import Tuple

from tracardi.service.adapter.cache.redis.redis_cache_adapter import redis_cache_adapter
from tracardi.service.storage.redis.collections import Collection


class Limiter:

    def __init__(self, limit: int, ttl: int):
        self._ttl = ttl
        self._limit = limit
        self._redis = redis_cache_adapter

    def limit(self, key: str) -> Tuple[bool, int]:

        key = f"{Collection.throttle}:{key}"

        req = self._redis.incr(key)
        if req == 1:
            self._redis.expire(key, self._ttl)
            ttl = self._ttl
        else:
            ttl = self._redis.ttl(key)

        return req <= self._limit, ttl
