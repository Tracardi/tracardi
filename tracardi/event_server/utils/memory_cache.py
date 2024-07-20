from datetime import datetime

import asyncio
from time import time
from typing import Any, Dict, List

from pydantic import BaseModel

from tracardi.context import get_context
from tracardi.exceptions.exception import ExpiredException
from tracardi.service.utils.date import seconds_to_minutes_seconds


class CacheItem(BaseModel):
    data: Any = None
    ttl: float = 60

    def __init__(self, **data: Any):
        if 'ttl' in data:
            data['ttl'] = time() + float(data['ttl'])

        super().__init__(**data)

    def expired(self):
        return time() > self.ttl


class MemoryCache:
    """
    The MemoryCache class implements an in-memory caching system with expiration capabilities for stored items.
    It operates by maintaining a dictionary as an internal memory buffer, where each key-value pair corresponds
    to a cache key and its associated CacheItem. Each CacheItem contains the actual data to be cached and a
    time-to-live (TTL) value indicating how long the data should remain valid.

    Here's a more streamlined explanation of how MemoryCache functions:
    Caching and Expiration Logic

    When an item is added to the cache, its TTL is converted into an absolute expiration timestamp. This
    timestamp is then used to determine if the item is still valid whenever it is accessed.
    The cache employs a lazy expiration mechanism. This means that items are only checked for expiration at the
    moment they are accessed. If an item's expiration timestamp is past the current time, it is considered expired
    and is automatically removed from the cache.

    To prevent the cache from indefinitely growing, a max_pool limit is set, indicating the maximum number of items
    the cache should ideally hold. When adding an item causes the cache to exceed this limit, the cache is purged
    of expired items. However, this mechanism does not guarantee that the cache size will be immediately reduced to
    below max_pool if all items within are still valid; it only removes those that have expired.
    """

    def __init__(self, name: str, max_pool=1000, allow_null_values=False, use_context: bool = True):
        self.memory_buffer: Dict[str, CacheItem] = {}
        self.name = name
        self.max_pool = max_pool
        self.counter = 0
        self.allow_null_values = allow_null_values
        self._use_context = use_context

    def _get_contextualized_key(self, key):

        if not self._use_context:
            return key

        try:
            context = get_context()
            return f"{hash(context)}-{key}"
        except ValueError:
            return key

    def __len__(self):
        return len(self.memory_buffer)

    def __contains__(self, key: str):
        key = self._get_contextualized_key(key)
        if key in self.memory_buffer:
            if self.memory_buffer[key].expired():
                del self.memory_buffer[key]

        return key in self.memory_buffer

    def is_expired(self, key: str) -> bool:
        key = self._get_contextualized_key(key)
        return (key in self.memory_buffer and self.memory_buffer[key].expired()) or key not in self.memory_buffer

    def __getitem__(self, item: str) -> [CacheItem, None]:
        item = self._get_contextualized_key(item)
        if item in self.memory_buffer:
            cache_item = self.memory_buffer[item]  # type: CacheItem
            if cache_item.expired():
                del self.memory_buffer[item]
                raise ExpiredException("MemoryCache item expired")
            return cache_item
        return None

    def __setitem__(self, key: str, value: CacheItem):
        key = self._get_contextualized_key(key)
        if not isinstance(value, CacheItem):
            raise ValueError("MemoryCache item must be CacheItem type.")
        self.memory_buffer[key] = value
        self.counter += 1
        if self.counter > self.max_pool:
            self.purge()

    def __delitem__(self, key):
        key = self._get_contextualized_key(key)
        if key in self.memory_buffer:
            del self.memory_buffer[key]

    def delete(self, key):
        if key in self:
            del self[key]

    def delete_all(self, keys: List[str]):
        for key in keys:
            del self[key]

    def purge(self):
        for key, value in self.memory_buffer.copy().items():
            if value.expired():
                del self.memory_buffer[key]

    def get_cached_items(self):
        return [{
            "expired": item.expired(),
            "ttl": seconds_to_minutes_seconds(item.ttl - datetime.now().timestamp()),
            "key_length": len(key)
        } for key, item in
            self.memory_buffer.items()]

    @staticmethod
    async def save(cache: 'MemoryCache', key, data, ttl):
        if asyncio.iscoroutine(data):
            data = await data  # Await the coroutine and store its result
        cache[key] = CacheItem(data=data, ttl=ttl)

    # TODO used in MemoryCache only
    @staticmethod
    async def cache(cache: 'MemoryCache', key, ttl, load_callable, awaitable, *args):
        if key not in cache:
            result = load_callable(*args)
            if awaitable:
                result = await result

            if result is None and not cache.allow_null_values:
                return None

            await MemoryCache.save(cache, key, data=result, ttl=ttl)

        return cache[key].data
