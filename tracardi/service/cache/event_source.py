from typing import Optional

from tracardi.config import memory_cache
from tracardi.domain.event_source import EventSource
from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.service.storage.mysql.interface import event_source_dao

@async_cache_for(memory_cache.source_ttl)
async def load_event_source_via_cache(source_id) -> Optional[EventSource]:
    return await event_source_dao.load_event_source_by_id(source_id)
