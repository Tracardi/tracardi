from tracardi.service.adapter.cache.cache_protocol import CacheProtocol
from tracardi.service.storage.redis.driver.redis_client import RedisClient


class RedisCacheAdapter(CacheProtocol):

    def __init__(self):
        self._client = RedisClient()

    def get(self, key: str):
        return self._client.get(key)

    def set(self, key: str, value, ex):
        return self._client.set(
            name=key,
            value=value,
            ex=ex
        )

    def mset(self, mapping):
        return self._client.mset(mapping)

    def delete(self, key: str):
        self._client.delete(key)


    def exists(self, key: str):
        self._client.exists(key)

    def expire(self, key, ttl):
        self._client.expire(key, ttl)

    def incr(self, key: str):
        return self._client.incr(key)

    def ttl(self, key: str):
        return self._client.ttl(key)

    def persist(self, key):
        return self._client.persist(key)

    def ping(self):
        return self._client.ping()


redis_cache_adapter:CacheProtocol = RedisCacheAdapter()