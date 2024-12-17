from typing import Optional, Tuple, List

from tracardi.domain.event_validator import EventValidator
from tracardi.service.cache.cache_tags import EVENT_VALIDATION_TAG
from tracardi.service.cache_change_tagger.change_tagger import invalidate_cache_on_update
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation
from tracardi.service.storage.mysql.service.event_validation_service import EventValidationService

evs = EventValidationService()


def _records(records, mapper) -> Tuple[List[EventValidator], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(mapper)), records.count()


async def load_all(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[EventValidator], int]:
    records = await evs.load_all(search, limit, offset)
    return _records(records,map_to_event_validation)


async def load_by_id(event_validation_id: str) -> Optional[EventValidator]:
    record = await evs.load_by_id(event_validation_id)
    return record.map_to_object(map_to_event_validation)


async def delete_by_id(event_validation_id: str) -> Tuple[bool, Optional[EventValidator]]:
    with invalidate_cache_on_update(*EVENT_VALIDATION_TAG):
        return await evs.delete_by_id(event_validation_id)


async def insert(event_validation: EventValidator):
    with invalidate_cache_on_update(*EVENT_VALIDATION_TAG):
        return await evs.insert(event_validation)


async def load_by_event_type(event_type: str, only_enabled: bool = True):
    records = await evs.load_by_event_type(event_type, only_enabled)
    return _records(records,map_to_event_validation)