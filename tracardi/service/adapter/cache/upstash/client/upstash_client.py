import os
from typing import Optional, Awaitable, Union, List

from upstash_redis import Redis

from tracardi.context import get_context
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.singleton import Singleton

logger = get_logger(__name__)


class UpStashRedisClient(metaclass=Singleton):
    def __init__(self):
        host = os.environ.get('UPSTASH_REDIS_HOST', None)
        token = os.environ.get('UPSTASH_REDIS_TOKEN', None)

        logger.debug(f"Connecting upstash redis at {host}")
        self.client = Redis(
            url="https://sincere-serval-37248.upstash.io",
            token="AZGAAAIjcDExM2NmMmE3ZDZkMGU0ZmU1YWZmNWJmNDg1MmZhODU2YnAxMA",
        rest_encoding=None)
        logger.info(f"Redis at {host} connected.")

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

    def smembers(self, name: str) -> Union[Awaitable[set], list]:
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
            ex:Optional[int] = None,
            px:Optional[int] = None,
            nx: Optional[bool] = None,
            xx:  Optional[bool] = None,
            keepttl: Optional[bool] = None,
            get: Optional[bool] = None,
            exat: Optional[int] = None,
            pxat: Optional[int] = None
    ):
        return self.client.set(self.get_tenant_prefix(name), value,
                               ex=ex, px=px, nx=nx, xx=xx, keepttl=keepttl, get=get, exat=exat, pxat=pxat)

    def delete(self, name):
        return self.client.delete(self.get_tenant_prefix(name))

    def incr(self, name, amount: int = 1):
        return self.client.incrby(self.get_tenant_prefix(name), amount)

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

    def publish(self, *args, **kwargs):
        return self.client.publish(*args, **kwargs)

    def mset(self, mapping):
        return self.client.mset(mapping)

    def persist(self, key):
        return self.client.persist(key)


upstash_redis_connection = UpStashRedisClient()
