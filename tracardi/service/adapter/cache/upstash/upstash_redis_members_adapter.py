from tracardi.service.adapter.cache.member_cache_protocol import MemberCacheProtocol
from tracardi.service.adapter.cache.upstash.client.upstash_client import UpStashRedisClient


class UpStashRedisMembersCacheAdapter(MemberCacheProtocol):
    def __init__(self):
        self._client = UpStashRedisClient()

    def smembers(self, name):
        return self._client.smembers(name)

    def sadd(self, name: str, *values):
        return self._client.sadd(name, *values)