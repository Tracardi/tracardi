from typing import Optional

import msgpack
import redis

from tracardi.service.cache_proxy.cache_capsule import CacheCapsule
from tracardi.service.cache_proxy.throttle import Throttler
from tracardi.service.cache_proxy.locker import distributed_lock

from tracardi.service.adapter.cache_adaper_selector import cache_adapter

_cache = cache_adapter()


class RedisProxyCache:
    def __init__(self, namespace: str, redis_url="redis://localhost:6379/0", throttle=1):
        self.throttler = Throttler(interval=throttle)
        self.namespace = namespace
        self.redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=False)  # Disable decoding

    def _namespace(self, key: str, suffix:str=None) -> str:
        if suffix:
            return f"{self.namespace}:{key}:{suffix}"
        return f"{self.namespace}:{key}"

    @staticmethod
    def _serialize(value) -> Optional[bytes]:
        return msgpack.packb(value, use_bin_type=True)

    @staticmethod
    def _deserialize(value):
        if value is None:
            return None
        return msgpack.unpackb(value, raw=False)

    def _get(self, key: str, suffix: str=None):
        print('get', self._namespace(key))
        value = _cache.get(self._namespace(key, suffix))
        return self._deserialize(value)

    def _set(self, key, value, suffix=None, ttl=None):
        value = self._serialize(value)
        _cache.set(self._namespace(key, suffix), value, ex=ttl)
        print('set', self._namespace(key, suffix))

    async def _load_and_update(self, key, func: CacheCapsule):
        with distributed_lock(_cache, self._namespace(key), expires=10) as locked:
            if locked:
                fresh_data = await self.throttler.call(func.func, *func.func_args, **func.func_kwargs)
                self._set(key, fresh_data, ttl=func.ttl)  # Update main cache
                self._set(key, fresh_data, suffix='stale')  # Update stale cache

    async def get(self, func: CacheCapsule):
        key = func.key()
        cached_data = self._get(key)
        if cached_data:
            print("returned cached", cached_data)
            # Data exists, return it immediately
            return cached_data

        # Update cache, lock and fetch data
        await self._load_and_update(key, func)

        print('Returns old value', self._get(f"{key}:stale"))
        # Return stale data or None if no stale data is available
        return self._get(key, suffix="stale")


