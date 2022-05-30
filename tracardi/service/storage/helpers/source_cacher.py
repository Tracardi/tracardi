import logging
from typing import Optional
from tracardi.config import memory_cache, tracardi
from tracardi.domain.entity import Entity
from tracardi.domain.event_source import EventSource
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver import storage

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class SourceCacher:

    def __init__(self):
        self._cache = MemoryCache()

    async def validate_source(self, source_id) -> Optional[EventSource]:
        entity = Entity(id=source_id)

        source = await self.get(entity)  # type: Optional[EventSource]
        if source is None:
            raise ValueError(f"Invalid event source `{source_id}`")

        if not source.enabled:
            raise ValueError("Event source disabled.")

        return source

    async def get(self, event_source: Entity) -> Optional[EventSource]:
        # todo This can make tracardi go "invalid event source"
        if event_source.id in self._cache:
            logger.info(f"Source `{event_source.id[0:5]}...` form cache. Valid for {memory_cache.source_ttl}s")
            return self._cache[event_source.id].data
        else:
            # Expired
            logger.info(f"Source `{event_source.id[0:5]}...` form storage.")
            event_source = await storage.driver.event_source.load(event_source.id)  # type: EventSource
            if event_source is not None:
                self._cache[event_source.id] = CacheItem(data=event_source, ttl=memory_cache.source_ttl)
                return event_source
            return None


source_cache = SourceCacher()
