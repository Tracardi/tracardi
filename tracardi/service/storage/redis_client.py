import logging
from typing import Optional, Awaitable, Union, List

# import aioredis
import redis

from tracardi.context import get_context
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.singleton import Singleton
from tracardi.config import redis_config, tracardi
from tracardi.service.storage.redis_connection_pool import get_redis_connection_pool

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


# class AsyncRedisClient(metaclass=Singleton):
#     def __init__(self):
#         host = redis_config.redis_host
#         password = redis_config.redis_password
#
#         if password is None:
#             self.client = aioredis.from_url(host)
#         else:
#             self.client = aioredis.from_url(host, password=password)
#
#         logger.info(f"Redis at {host} connected.")


class RedisClient(metaclass=Singleton):
    def __init__(self):
        uri = redis_config.get_redis_with_password()
        logger.debug(f"Connecting redis vai pool at {uri}")
        self.client = redis.Redis(connection_pool=get_redis_connection_pool(redis_config))
        logger.info(f"Redis at {redis_config.redis_host} connected.")

    @staticmethod
    def get_tenant_prefix(name):
        return f"{get_context().tenant}:{name}"

    def hexists(self, name: str, key: str) -> Union[Awaitable[bool], bool]:
        return self.client.hexists(name, key)

    def hget(
            self, name: str, key: str
    ):
        return self.client.hget(self.get_tenant_prefix(name), key)

    def hset(self,
             name: str,
             key: Optional[str] = None,
             value: Optional[str] = None,
             mapping: Optional[dict] = None,
             items: Optional[list] = None) -> Union[Awaitable[int], int]:
        return self.client.hset(self.get_tenant_prefix(name), key, value, mapping, items)

    def hdel(self, name: str, *keys: List) -> Union[Awaitable[int], int]:
        return self.client.hdel(self.get_tenant_prefix(name), *keys)

    def sadd(self, name: str, *values) -> Union[Awaitable[int], int]:
        return self.client.sadd(self.get_tenant_prefix(name), *values)

    def smembers(self, name: str) -> Union[Awaitable[list], list]:
        return self.client.smembers(self.get_tenant_prefix(name))

    def ttl(self, name):
        return self.client.ttl(self.get_tenant_prefix(name))

    def exists(self, name):
        return self.client.exists(self.get_tenant_prefix(name))

    def get(self, name):
        return self.client.get(self.get_tenant_prefix(name))

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
        return self.client.set(self.get_tenant_prefix(name), value, ex, px, nx, xx, keepttl, get, exat, pxat)

    def delete(self, name):
        return self.client.delete(self.get_tenant_prefix(name))

    def incr(self, name, amount: int = 1):
        return self.client.incr(self.get_tenant_prefix(name), amount)

    def expire(
            self,
            name,
            time,
            nx: bool = False,
            xx: bool = False,
            gt: bool = False,
            lt: bool = False,
    ):
        return self.client.expire(self.get_tenant_prefix(name), time, nx, xx, gt, lt)

    def ping(self, **kwargs):
        return self.client.ping(**kwargs)

    def pubsub(self, **kwargs):
        return self.client.pubsub(**kwargs)
