import aioredis
import redis
from tracardi.service.singleton import Singleton


class AsyncRedisClient(metaclass=Singleton):
    def __init__(self, host):
        self.client = aioredis.from_url(host)


class RedisClient(metaclass=Singleton):
    def __init__(self, host):
        self.client = redis.from_url(host)
