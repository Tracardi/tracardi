from typing import Optional, Tuple, List
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile
from tracardi.service.storage.mysql.service.event_to_profile_service import EventToProfileMappingService

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


async def load_event_to_profile_mapping_by_id(mapping_id: str) -> SelectResult:
    return await etpms.load_by_id(mapping_id)


async def delete_event_to_profile_mapping_by_id(mapping_id: str) -> Tuple[bool, Optional[EventToProfile]]:
    return await etpms.delete_by_id(mapping_id)


async def insert_event_to_profile_mapping(mapping: EventToProfile):
    return await etpms.insert(mapping)


async def load_event_to_profile_mapping_by_type(event_type: str, enabled_only: bool = False) -> Tuple[List[EventToProfile], int]:
    records = await etpms.load_by_type(
        event_type, enabled_only
    )
    return _records(records)
