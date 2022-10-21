from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.live_segment import LiveSegment
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager, StorageForBulk, StorageFor


async def load_segments(event_type, limit=500) -> StorageRecords:
    return await storage_manager(index="segment"). \
        load_by_query_string("(NOT _exists_:eventType) OR eventType: \"{}\"".format(event_type, limit))


async def load_all(start: int = 0, limit: int = 100) -> StorageRecords:
    return await StorageForBulk().index('live-segment').load(start, limit)


async def refresh():
    return await storage_manager('live-segment').refresh()


async def flush():
    return await storage_manager('live-segment').flush()


async def save(data: dict):
    return await storage_manager('live-segment').upsert(data)


async def delete_by_id(id):
    return await storage_manager('live-segment').delete(id)


async def load_by_id(id) -> Optional[LiveSegment]:
    entity = Entity(id=id)
    return await StorageFor(entity).index('live-segment').load(LiveSegment)
