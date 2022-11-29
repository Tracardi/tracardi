from typing import Optional

from tracardi.domain.event_source import EventSource
from tracardi.domain.session import Session
from tracardi.domain.storage_record import StorageRecords
from tracardi.event_server.utils.memory_cache import MemoryCache
from tracardi.service.singleton import Singleton
from tracardi.service.storage.driver import storage


class CacheManager(metaclass=Singleton):
    _cache = {
        'SESSION': MemoryCache(),
        'EVENT_SOURCE': MemoryCache(),
        'EVENT_VALIDATION': MemoryCache()
    }

    def session_cache(self) -> MemoryCache:
        return self._cache['SESSION']

    def event_source_cache(self) -> MemoryCache:
        return self._cache['EVENT_SOURCE']

    def event_validation_cache(self) -> MemoryCache:
        return self._cache['EVENT_VALIDATION']

    # Caches

    async def session(self, session_id, ttl) -> Optional[Session]:
        """
        Session cache
        """
        if ttl > 0:
            return await MemoryCache.cache(
                self.session_cache(),
                session_id,
                ttl,
                storage.driver.session.load_by_id,
                True,
                session_id
            )
        return await storage.driver.session.load_by_id(session_id)

    async def event_source(self, event_source_id, ttl) -> Optional[EventSource]:
        """
        Event source cache
        """
        if ttl > 0:
            return await MemoryCache.cache(
                self.event_source_cache(),
                event_source_id,
                ttl,
                storage.driver.event_source.load,
                True,
                event_source_id
            )
        return await storage.driver.event_source.load(event_source_id)

    async def event_validation(self, event_type, ttl) -> StorageRecords:
        """
        Event validation schema cache
        """
        if ttl > 0:
            return await MemoryCache.cache(
                self.event_validation_cache(),
                event_type,
                ttl,
                storage.driver.event_validation.load_by_event_type,
                True,
                event_type)
        return await storage.driver.event_validation.load_by_event_type(event_type)
