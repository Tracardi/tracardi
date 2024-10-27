from typing import Optional

from tracardi.config import memory_cache
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.interface import event_mapping_dao


@AsyncCache(memory_cache.event_mapping_cache_ttl,
            timeout=.5,
            max_one_cache_fill_every=.1,
            allow_null_values=True,
            return_cache_on_error=True
            )
async def load_event_mapping(event_type_id: str) -> Optional[EventTypeMetadata]:
    mappings, _ = await event_mapping_dao.load_by_event_type_id(event_type_id, only_enabled=True)
    if not mappings:
        return None
    return mappings
