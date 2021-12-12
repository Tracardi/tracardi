from typing import Optional, Union
from tracardi.config import memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.event_source import EventSource
from tracardi.domain.resource import ResourceRecord
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.service.storage.driver import storage
from tracardi.service.storage.factory import StorageFor


class SourceCacher:

    def __init__(self):
        self._cache = MemoryCache()

    async def validate_source(self, source_id) -> ResourceRecord:
        entity = Entity(id=source_id)

        source = await self.get(entity)  # type: Optional[ResourceRecord]
        if source is None:
            raise ValueError("Invalid event source.")

        if not source.enabled:
            raise ValueError("Event source disabled.")

        return source

    async def get(self, event_source: Entity) -> Optional[Union[EventSource]]:
        if 'event-source' in self._cache:
            return self._cache['event-source'].data
        else:
            # Expired
            event_source = await storage.driver.event_source.load(event_source.id)  # type: EventSource
            if event_source is not None:
                self._cache['event-source'] = CacheItem(data=event_source, ttl=memory_cache.source_ttl)
                return event_source
            return None


source_cache = SourceCacher()
