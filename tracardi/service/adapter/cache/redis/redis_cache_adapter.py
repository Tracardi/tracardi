import msgpack

from tracardi.service.adapter.cache.cache_protocol import CacheProtocol
from tracardi.service.adapter.cache.redis.client.redis_client import RedisClient


class RedisCacheAdapter(CacheProtocol):

    def __init__(self):
        self._client = RedisClient()

    def get(self, key: str):
        return self._client.get(key)

    def get_msgpack(self, key: str):
        value = self._client.get(key)
        if value is None:
            return None

        return msgpack.unpackb(value)

    def set(self, key: str, value, ex=None, nx: bool = None):
        return self._client.set(
            name=key,
            value=value,
            ex=ex,
            nx=nx
        )

    def set_msgpack(self, key, value, ex=None):
        return self._client.set(
            name=key,
            value=msgpack.packb(value, default=str),
            ex=ex
        )

    def mset(self, mapping):
        return self._client.mset(mapping)

    def delete(self, key: str, skip_tenant: bool = False):
        return self._client.delete(key, skip_tenant)

    def exists(self, key: str):
        return self._client.exists(key)

    def expire(self, key, ttl):
        return self._client.expire(key, ttl)

    def incr(self, key: str):
        return self._client.incr(key)

    def ttl(self, key: str):
        return self._client.ttl(key)

    def persist(self, key):
        return self._client.persist(key)

    def ping(self):
        return self._client.ping()

    def scan(self, match=None, count=None):
        return self._client.scan(match, count)
