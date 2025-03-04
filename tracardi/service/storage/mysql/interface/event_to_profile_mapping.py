from typing import Optional, Tuple, List
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile
from tracardi.service.storage.mysql.service.event_to_profile_service import EventToProfileMappingService
from tracardi.config import memory_cache
from tracardi.common.decorator.async_cache import AsyncCache
from tracardi.service.storage.mysql.utils.select_result import SelectResult

etpms = EventToProfileMappingService()


def _records(records: SelectResult) -> Tuple[List[EventToProfile], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_event_to_profile)), records.count()


async def load_all_event_to_profile_mapping(search: Optional[str] = None,
                                            limit: Optional[int] = None,
                                            offset: Optional[int] = None) -> Tuple[List[EventToProfile], int]:
    records = await etpms.load_all(search, limit, offset)
    return _records(records)


async def load_enabled_event_to_profile_mapping() -> List[EventToProfile]:
    records = await etpms.load_enabled()

    if not records.exists():
        return []

    return list(records.map_to_objects(map_to_event_to_profile))


async def load_event_to_profile_mapping_by_id(mapping_id: str) -> Optional[EventToProfile]:
    record = await etpms.load_by_id(mapping_id)

    if not record.exists():
        return None

    return record.map_to_object(map_to_event_to_profile)



async def load_event_to_profile_mapping_by_type(event_type: str, enabled_only: bool = False) -> Tuple[
    List[EventToProfile], int]:
    records = await etpms.load_by_type(
        event_type, enabled_only
    )
    return _records(records)


# Cache


@AsyncCache(memory_cache.event_to_profile_coping_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_event_to_profile(event_type_id: str) -> List[EventToProfile]:
    mappings, total = await load_event_to_profile_mapping_by_type(event_type_id, enabled_only=True)
    if not mappings:
        return []
    return mappings


async def delete_event_to_profile_mapping_by_id(mapping_id: str) -> Tuple[bool, Optional[EventToProfile]]:
    return await etpms.delete_by_id(mapping_id)


async def insert_event_to_profile_mapping(mapping: EventToProfile):
    return await etpms.insert(mapping)
