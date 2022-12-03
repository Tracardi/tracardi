from typing import Optional, List

from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.domain.event_source import EventSource
from tracardi.domain.session import Session
from tracardi.domain.storage_record import StorageRecords
from tracardi.event_server.utils.memory_cache import MemoryCache
from tracardi.service.singleton import Singleton
from tracardi.service.storage.driver import storage


class CacheManager(metaclass=Singleton):
    _cache = {
        'SESSION': MemoryCache("session", max_pool=1000),
        'EVENT_SOURCE': MemoryCache("event-source", max_pool=100),
        'EVENT_VALIDATION': MemoryCache("event-validation", max_pool=500),
        'EVENT_TAG': MemoryCache("event-tags", max_pool=200),
        'EVENT_RESHAPING': MemoryCache("event-reshaping", max_pool=200)
    }

    def session_cache(self) -> MemoryCache:
        return self._cache['SESSION']

    def event_source_cache(self) -> MemoryCache:
        return self._cache['EVENT_SOURCE']

    def event_validation_cache(self) -> MemoryCache:
        return self._cache['EVENT_VALIDATION']

    def event_tag_cache(self) -> MemoryCache:
        return self._cache['EVENT_TAG']

    def event_reshaping_cache(self) -> MemoryCache:
        return self._cache['EVENT_RESHAPING']

    # Caches

    async def session(self, session_id, ttl) -> Optional[Session]:
        """
        Session cache
        """
        if ttl > 0:
            return await MemoryCache.cache(
                self.session_cache(),
                True,
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
                False,
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
                True,
                event_type,
                ttl,
                storage.driver.event_validation.load_by_event_type,
                True,
                event_type)
        return await storage.driver.event_validation.load_by_event_type(event_type)

    async def event_tag(self, event_type, ttl):
        if ttl > 0:
            return await MemoryCache.cache(
                self.event_tag_cache(),
                True,
                event_type,
                ttl,
                storage.driver.event_management.get_event_type_metadata,
                True,
                event_type)

        return await storage.driver.event_management.get_event_type_metadata(event_type)

    @staticmethod
    async def _load_and_convert_reshaping(event_type) -> Optional[List[EventReshapingSchema]]:
        reshape_schemas = await storage.driver.event_reshaping.load_by_event_type(event_type)
        if reshape_schemas:
            return reshape_schemas.to_domain_objects(EventReshapingSchema)
        return None

    async def event_reshaping(self, event_type, ttl) -> Optional[List[EventReshapingSchema]]:
        if ttl > 0:
            return await MemoryCache.cache(
                self.event_reshaping_cache(),
                True,
                event_type,
                ttl,
                self._load_and_convert_reshaping,
                True,
                event_type)
        return await self._load_and_convert_reshaping(event_type)