from tracardi.service.adapter.cache.member_cache_protocol import MemberCacheProtocol
from tracardi.service.adapter.cache.redis.client.redis_client import RedisClient


class RedisMembersCacheAdapter(MemberCacheProtocol):
    def __init__(self):
        self._client = RedisClient()

    def smembers(self, name):
        return self._client.smembers(name)

    def sadd(self, name: str, *values):
        return self._client.sadd(name, *values)