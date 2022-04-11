import aioredis
import redis
from tracardi.service.singleton import Singleton
from tracardi.config import redis_config


class AsyncRedisClient(metaclass=Singleton):
    def __init__(self, host):
        self.client = aioredis.from_url(host)


class RedisClient(metaclass=Singleton):
    def __init__(self):
        host = redis_config.redis_host
        password = redis_config.redis_password

        if password is None:
            self.client = redis.from_url(host)
        else:
            self.client = redis.from_url(host, password=password)
