from tracardi.service.storage.redis_client import RedisClient
import msgpack


class RedisCache:

    def __init__(self, ttl, prefix):
        self._redis = RedisClient()
        self.ttl = ttl
        self.prefix = prefix

    def __setitem__(self, key, value):
        self._redis.set(f"{self.prefix}{key}", msgpack.packb(value), ex=self.ttl)

    def __getitem__(self, key):
        value = self._redis.get(f"{self.prefix}{key}")
        if value is None:
            return None

        return msgpack.unpackb(value)

    def __delitem__(self, key):
        self._redis.delete(f"{self.prefix}{key}")

    def __contains__(self, key):
        return self._redis.exists(f"{self.prefix}{key}")

    def refresh(self, key):
        self._redis.expire(f"{self.prefix}{key}", self.ttl)
