from time import time
from typing import Any

from pydantic import BaseModel

from tracardi.exceptions.exception import ExpiredException


class CacheItem(BaseModel):
    data: Any
    ttl: int = 60

    def __init__(self, **data: Any):
        if 'ttl' in data:
            data['ttl'] = time() + data['ttl']
        super().__init__(**data)

    def expired(self):
        return time() > self.ttl


class MemoryCache:

    def __init__(self):
        self.memory_buffer = {}

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
