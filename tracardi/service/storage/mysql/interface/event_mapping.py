from typing import Tuple, Optional, List

from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.service.storage.mysql.mapping.event_to_event_mapping import map_to_event_mapping
from tracardi.service.storage.mysql.service.event_mapping_service import EventMappingService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

ems = EventMappingService()

def _records(records: SelectResult) -> Tuple[List[EventTypeMetadata], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_event_mapping)), records.count()

async def load_all(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[EventTypeMetadata], int]:
    records = await ems.load_all(search, limit, offset)
    return _records(records)


async def load_by_id(event_mapping_id: str) -> Optional[EventTypeMetadata]:
    record = await ems.load_by_id(event_mapping_id)
    return record.map_to_object(map_to_event_mapping)


async def delete_by_id(event_mapping_id: str) -> Tuple[bool, Optional[EventTypeMetadata]]:
    return await ems.delete_by_id(event_mapping_id)


async def insert(event_type_metadata: EventTypeMetadata):
    return await ems.insert(event_type_metadata)


async def load_by_event_type(event_type: str, only_enabled: bool = True) ->  Tuple[List[EventTypeMetadata], int]:
    records = await ems.load_by_event_type(event_type, only_enabled)
    return _records(records)


async def load_by_event_types(event_types: List[str], only_enabled: bool = True) -> Tuple[List[EventTypeMetadata], int]:
    records = await ems.load_by_event_types(event_types, only_enabled)
    return _records(records)


async def load_by_event_type_id(event_type_id: str, only_enabled: bool = True) ->  Optional[EventTypeMetadata]:
    record = await ems.load_by_event_type_id(event_type_id, only_enabled)
    return record.map_first_to_object(map_to_event_mapping)
