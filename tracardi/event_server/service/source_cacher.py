from typing import Optional, Union
from tracardi.config import memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.source import ResourceRecord
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem


class SourceCacher:

    def __init__(self):
        self._cache = MemoryCache()

    async def validate_source(self, source_id) -> ResourceRecord:
        entity = Entity(id=source_id)

        source = await self.get(entity)  # type: Optional[ResourceRecord]
        if source is None:
            raise ValueError("Invalid source.")

        if not source.enabled:
            raise ValueError("Source disabled.")

        return source

    async def get(self, resource: Entity) -> Optional[Union[ResourceRecord]]:
        if 'source' in self._cache:
            resource = self._cache['source'].data
            return resource
        else:
            # Expired
            resource = await resource.storage("source").load(ResourceRecord)  # type: ResourceRecord
            if resource is not None:
                self._cache['source'] = CacheItem(data=resource, ttl=memory_cache.source_ttl)
                return resource
            return None


source_cache = SourceCacher()
