from fastapi import APIRouter
from fastapi import HTTPException

from tracardi.config import memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.source import Source, SourceRecord
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem


router = APIRouter()


class SourceCacher:

    def __init__(self):
        self._cache = MemoryCache()

    async def validate_source(self, source_id) -> Source:
        entity = Entity(id=source_id)

        source = await self.get(entity)  # type: Source
        if source is None:
            raise HTTPException(detail="Access denied. Invalid source.", status_code=401)

        if not source.enabled:
            raise HTTPException(detail="Access denied. Source disabled.", status_code=404)

        return source

    async def get(self, source: Entity):
        if 'source' in self._cache:
            source = self._cache['source'].data
            return source
        else:
            # Expired
            source = await source.storage("source").load(SourceRecord)  # type: SourceRecord
            if source is not None:
                self._cache['source'] = CacheItem(data=source, ttl=memory_cache.source_ttl)
                return source
            return None


source_cache = SourceCacher()
