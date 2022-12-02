import asyncio
from time import time
from typing import Any, Dict

from pydantic import BaseModel

from tracardi.exceptions.exception import ExpiredException


class CacheItem(BaseModel):
    data: Any
    ttl: float = 60

    def __init__(self, **data: Any):
        if 'ttl' in data:
            data['ttl'] = time() + float(data['ttl'])

        super().__init__(**data)

    def expired(self):
        return time() > self.ttl


class MemoryCache:

    def __init__(self, name: str, max_pool=1000):
        self.memory_buffer: Dict[str, CacheItem] = {}
        self.name = name
        self.max_pool = max_pool
        self.counter = 0

    def __len__(self):
        return len(self.memory_buffer)

    def __contains__(self, key: str):
        if key in self.memory_buffer:
            if self.memory_buffer[key].expired():
                del self.memory_buffer[key]

        return key in self.memory_buffer

    def __getitem__(self, item: str) -> [CacheItem, None]:
        if item in self.memory_buffer:
            cache_item = self.memory_buffer[item]  # type: CacheItem
            if cache_item.expired():
                del self.memory_buffer[item]
                raise ExpiredException("MemoryCache item expired")
            return cache_item
        return None

    def __setitem__(self, key: str, value: CacheItem):
        if not isinstance(value, CacheItem):
            raise ValueError("MemoryCache item must be CacheItem type.")
        self.memory_buffer[key] = value
        self.counter += 1
        if self.counter > self.max_pool:
            self.purge()

    def __delitem__(self, key):
        if key in self.memory_buffer:
            del self.memory_buffer[key]

    def purge(self):
        for key, value in self.memory_buffer.copy().items():
            if value.expired():
                del self.memory_buffer[key]

    @staticmethod
    async def cache(cache: 'MemoryCache', null_cache_allowed, key, ttl, load_callable, awaitable, *args):
        if key not in cache:
            result = load_callable(*args)
            if awaitable:
                result = await result

            if result is None and not null_cache_allowed:
                return None

            cache[key] = CacheItem(data=result, ttl=ttl)

        return cache[key].data
