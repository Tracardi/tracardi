from typing import Tuple

from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis.driver.redis_client import RedisClient


class Limiter:

    def __init__(self, limit: int, ttl: int):
        self._ttl = ttl
        self._limit = limit
        self._redis = RedisClient()

    def limit(self, key: str) -> Tuple[bool, int]:

        key = f"{Collection.throttle}:{key}"

        req = self._redis.incr(key)
        if req == 1:
            self._redis.expire(key, self._ttl)
            ttl = self._ttl
        else:
            ttl = self._redis.ttl(key)

        return req <= self._limit, ttl
