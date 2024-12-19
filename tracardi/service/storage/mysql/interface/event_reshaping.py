from typing import Optional, Tuple, List

from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping
from tracardi.service.storage.mysql.service.event_reshaping_service import EventReshapingService
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.config import memory_cache
from tracardi.service.decorators.async_cache import AsyncCache

ers = EventReshapingService()


def _records(records: SelectResult) -> Tuple[List[EventReshapingSchema], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_event_reshaping)), records.count()


async def load_all_event_reshaping(search: str = None, limit: int = None, offset: int = None) -> Tuple[
    List[EventReshapingSchema], int]:
    records = await ers.load_all(search, limit, offset)
    return _records(records)


async def load_event_reshaping_by_id(event_reshaping_id: str) -> Optional[EventReshapingSchema]:
    records = await ers.load_by_id(event_reshaping_id)
    return records.map_first_to_object(map_to_event_reshaping)


async def load_event_reshaping_by_event_type(event_type: str, only_enabled: bool = True):
    records = await ers.load_by_event_type(event_type, only_enabled)
    return _records(records)


# Cache

@AsyncCache(memory_cache.event_reshaping_cache_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            allow_null_values=True,
            return_cache_on_error=True
            )
async def load_and_convert_reshaping(event_type: str) -> Optional[List[EventReshapingSchema]]:
    reshape_schemas, total = await load_event_reshaping_by_event_type(event_type)
    if reshape_schemas:
        return reshape_schemas
    return None


async def delete_event_reshaping_by_id(event_reshaping_id: str) -> Tuple[bool, Optional[EventReshapingSchema]]:
    return await ers.delete_by_id(event_reshaping_id)


async def insert_event_reshaping(event_reshaping: EventReshapingSchema):
    return await ers.insert(event_reshaping)
