from typing import Optional, Any

from tracardi.service.storage.redis.driver.redis_client import RedisClient
import msgpack


class RedisCache:

    def __init__(self, ttl):
        self._redis = RedisClient()
        self.ttl = ttl

    def set(self, key: str, value: Any, collection: str):
        self._redis.set(
            f"{collection}{key}",
            msgpack.packb(value),
            ex=self.ttl
        )

    def mset(self, mapping):
        return self._redis.mset(mapping)

    def get(self, key:str, collection: str) -> Optional[Any]:
        value = self._redis.get(f"{collection}{key}")
        if value is None:
            return None

        return msgpack.unpackb(value)

    def delete(self, key: str, collection: str):
        self._redis.delete(f"{collection}{key}")

    def has(self, key, collection):
        return self._redis.exists(f"{collection}{key}")

    def refresh(self, key, collection):
        self._redis.expire(f"{collection}{key}", self.ttl)

    def expire(self, key, ttl):
        self._redis.expire(key, ttl)

    def persist(self, key):
        self._redis.persist(key)

    def get_ttl(self, key:str, collection:str):
        return self._redis.ttl(f"{collection}{key}")
