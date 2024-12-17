from typing import Optional

import msgpack

from tracardi.service.cache_proxy.cache_capsule import CacheCapsule
from tracardi.service.cache_proxy.throttle import Throttler
from tracardi.service.cache_proxy.locker import distributed_lock

from tracardi.service.adapter.cache_adaper_selector import cache_adapter

_cache = cache_adapter()
_throttler = Throttler('cache',
                      max_wait_between_calls=.1)

class CacheProxy:
    def __init__(self, namespace: str, lock_expires:int=60):
        self.lock_expires = lock_expires
        self.namespace = namespace

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
        value = _cache.get(self._namespace(key, suffix))
        return self._deserialize(value)

    def _set(self, key, value, suffix=None, ttl=None):
        value = self._serialize(value)
        _cache.set(self._namespace(key, suffix), value, ex=ttl)

    async def _load_and_update(self, key, func: CacheCapsule):
        with distributed_lock(_cache, self._namespace(key), expires=self.lock_expires) as locked:
            if locked:
                fresh_data = await func.run()
                self._set(key, fresh_data, ttl=func.cache_ttl)  # Update distributed cache
                return fresh_data
            # Return from distributed
            return self._get(key)

    async def get(self, func: CacheCapsule):
        key = str(hash(func))

        cached_data = self._get(key)
        if cached_data:
            # Data exists, return it immediately from distributed
            return cached_data

        # Use throttler to protect distributed cache

        return await _throttler.call(func.max_no_exec_time, self._load_and_update, key, func)



