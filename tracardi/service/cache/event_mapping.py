from typing import Optional

from tracardi.config import memory_cache
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.service.storage.mysql.mapping.event_to_event_mapping import map_to_event_mapping
from tracardi.service.storage.mysql.service.event_mapping_service import EventMappingService

@async_cache_for(memory_cache.event_metadata_cache_ttl)
async def load_event_mapping(event_type_id: str) -> Optional[EventTypeMetadata]:
    ems = EventMappingService()

    record = await ems.load_by_event_type_id(event_type_id, only_enabled=True)
    if not record.exists():
        return None
    return record.map_to_object(map_to_event_mapping)