from typing import Optional
from tracardi.domain.live_segment import LiveSegment
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager


async def load_segments(event_type, limit=500) -> StorageRecords:
    return await storage_manager(index="segment"). \
        load_by_query_string("(NOT _exists_:eventType) OR eventType: \"{}\"".format(event_type, limit))


async def load_all(start: int = 0, limit: int = 100) -> StorageRecords:
    return await storage_manager('live-segment').load_all(start, limit)


async def load_live_segments_by(type: str, limit: int = 1000) -> StorageRecords:
    return await storage_manager('live-segment').load_by_values(
        [('type', type)],
        limit=limit
    )


async def refresh():
    return await storage_manager('live-segment').refresh()


async def flush():
    return await storage_manager('live-segment').flush()


async def save(data: dict):
    return await storage_manager('live-segment').upsert(data)


async def delete_by_id(id):
    sm = storage_manager('live-segment')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def load_by_id(id) -> Optional[LiveSegment]:
    return LiveSegment.create(await storage_manager('live-segment').load(id))
