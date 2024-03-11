from typing import List

from tracardi.config import memory_cache
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile
from tracardi.service.storage.mysql.service.event_to_profile_service import EventToProfileMappingService
from tracardi.service.decorators.function_memory_cache import async_cache_for

@async_cache_for(memory_cache.event_to_profile_coping_ttl)
async def load_event_to_profile(event_type_id: str) -> List[EventToProfile]:
    etpms = EventToProfileMappingService()
    records = await etpms.load_by_type(event_type_id, enabled_only=True)
    if not records.exists():
        return []
    return list(records.map_to_objects(map_to_event_to_profile))