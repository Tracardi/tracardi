from typing import List

from tracardi.config import memory_cache
from tracardi.domain.event_validator import EventValidator
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation
from tracardi.service.storage.mysql.service.event_validation_service import EventValidationService
from tracardi.service.decorators.function_memory_cache import async_cache_for

@async_cache_for(memory_cache.event_validation_cache_ttl)
async def load_event_validation(event_type: str) -> List[EventValidator]:
    evs = EventValidationService()
    return list((await evs.load_by_event_type(event_type, only_enabled=True)).map_to_objects(map_to_event_validation))