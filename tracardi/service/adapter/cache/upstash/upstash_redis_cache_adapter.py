import base64

import msgpack

from tracardi.service.adapter.cache.cache_protocol import CacheProtocol
from tracardi.service.adapter.cache.upstash.client.upstash_client import UpStashRedisClient


class UpStashRedisCacheAdapter(CacheProtocol):

    def __init__(self):
        self._client = UpStashRedisClient()

    def get(self, key: str):
        return self._client.get(key)

    def set(self, key: str, value, ex=None, nx:bool=None):
        return self._client.set(
            name=key,
            value=value,
            ex=ex,
            nx=nx
        )

    def get_msgpack(self, key: str):
        value = self._client.get(key)

        if value is None:
            return None

        value = base64.b64decode(value)
        return msgpack.unpackb(value)

    def set_msgpack(self, key, value, ex=None):
        v = msgpack.packb(value)
        v = base64.b64encode(v).decode('utf-8')
        return self.set(
            key=key,
            value=v,
            ex=ex
        )

    def mset(self, mapping):
        return self._client.mset(mapping)

    def delete(self, key: str):
        return self._client.delete(key)

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
