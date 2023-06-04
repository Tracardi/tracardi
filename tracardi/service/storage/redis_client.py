import logging
from typing import Optional, Awaitable, Union, List

import aioredis
import redis

from tracardi.exceptions.log_handler import log_handler
from tracardi.service.singleton import Singleton
from tracardi.config import redis_config, tracardi

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class AsyncRedisClient(metaclass=Singleton):
    def __init__(self):
        host = redis_config.redis_host
        password = redis_config.redis_password

        if password is None:
            self.client = aioredis.from_url(host)
        else:
            self.client = aioredis.from_url(host, password=password)

        logger.info(f"Redis at {host} connected.")


class RedisClient(metaclass=Singleton):
    def __init__(self):
        uri = redis_config.get_redis_with_password()
        logger.debug(f"Connecting redis at {uri}")
        self.client = redis.from_url(uri)
        logger.info(f"Redis at {redis_config.redis_host} connected.")

    def hexists(self, name: str, key: str) -> Union[Awaitable[bool], bool]:
        return self.client.hexists(name, key)

    def hget(
            self, name: str, key: str
    ):
        return self.client.hget(name, key)

    def hset(self,
             name: str,
             key: Optional[str] = None,
             value: Optional[str] = None,
             mapping: Optional[dict] = None,
             items: Optional[list] = None) -> Union[Awaitable[int], int]:
        return self.client.hset(name, key, value, mapping, items)

    def hdel(self, name: str, *keys: List) -> Union[Awaitable[int], int]:
        return self.client.hdel(name, *keys)

    def sadd(self, name: str, *values) -> Union[Awaitable[int], int]:
        return self.client.sadd(name, *values)

    def smembers(self, name: str) -> Union[Awaitable[list], list]:
        return self.client.smembers(name)

    def ttl(self, name):
        return self.client.ttl(name)

    def exists(self, *names):
        return self.client.exists(*names)

    def get(self, name):
        return self.client.get(name)

    def set(
            self,
            name,
            value,
            ex=None,
            px=None,
            nx: bool = False,
            xx: bool = False,
            keepttl: bool = False,
            get: bool = False,
            exat=None,
            pxat=None,
    ):
        return self.client.set(name, value, ex, px, nx, xx, keepttl, get, exat, pxat)

    def delete(self, *names):
        return self.client.delete(*names)

    def incr(self, name, amount: int = 1):
        return self.client.incr(name, amount)

    def expire(
            self,
            name,
            time,
            nx: bool = False,
            xx: bool = False,
            gt: bool = False,
            lt: bool = False,
    ):
        return self.client.expire(name, time, nx, xx, gt, lt)

    def ping(self, **kwargs):
        return self.client.ping( **kwargs)

    def pubsub(self, **kwargs):
        return self.client.pubsub(**kwargs)
