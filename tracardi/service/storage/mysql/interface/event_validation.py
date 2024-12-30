from typing import Optional, Tuple, List

from tracardi.domain.event_validator import EventValidator
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation
from tracardi.service.storage.mysql.service.event_validation_service import EventValidationService
from tracardi.config import memory_cache
from tracardi.common.decorator.async_cache import AsyncCache

evs = EventValidationService()


def _records(records, mapper) -> Tuple[List[EventValidator], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(mapper)), records.count()


async def load_all(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[EventValidator], int]:
    records = await evs.load_all(search, limit, offset)
    return _records(records, map_to_event_validation)


async def load_by_id(event_validation_id: str) -> Optional[EventValidator]:
    record = await evs.load_by_id(event_validation_id)
    return record.map_to_object(map_to_event_validation)


async def load_by_event_type(event_type: str, only_enabled: bool = True):
    records = await evs.load_by_event_type(event_type, only_enabled)
    return _records(records, map_to_event_validation)


# Cache
@AsyncCache(memory_cache.event_validation_cache_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_event_validation(event_type: str) -> List[EventValidator]:
    records, _ = await load_by_event_type(event_type, only_enabled=True)
    return records


async def delete_by_id(event_validation_id: str) -> Tuple[bool, Optional[EventValidator]]:
    return await evs.delete_by_id(event_validation_id)


async def insert(event_validation: EventValidator):
    return await evs.insert(event_validation)
