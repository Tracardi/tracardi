from typing import List, Tuple, Optional

from tracardi.domain.destination import Destination
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination
from tracardi.service.storage.mysql.service.destination_service import DestinationService

ds = DestinationService()


def _records(records) -> Tuple[List[Destination], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_destination)), records.count()


async def load_destination_by_id(id: str) -> Optional[Destination]:
    record = await ds.load_by_id(id)

    if not record.exists():
        return None

    return record.map_to_object(map_to_destination)


async def load_all_destinations(query, start, limit) -> Tuple[List[Destination], int]:
    records = await ds.load_all(query, start, limit)
    return _records(records)


async def load_destinations_for_event_type(event_type: str, source_id: str) -> Tuple[List[Destination], int]:
    records = await ds.load_event_destinations(event_type, source_id)
    return _records(records)


async def load_destinations_for_profile():
    records = await ds.load_profile_destinations()
    return _records(records)


async def insert_destination(destination: Destination):
    return await ds.insert(destination)


async def delete_destination(id: str):
    await ds.delete_by_id(id)
