from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, StorageForBulk
from typing import Optional


async def refresh():
    return await storage_manager('event-reshaping').refresh()


async def flush():
    return await storage_manager('event-reshaping').flush()


async def upsert(data: EventReshapingSchema):
    return await storage_manager('event-reshaping').upsert(data, replace_id=True)


async def load(id: str) -> Optional[EventReshapingSchema]:
    result: EventReshapingSchema = await StorageFor(Entity(id=id)).index("event-reshaping").load(
        EventReshapingSchema
    )
    return result


async def load_all(limit=100) -> StorageRecords:
    return await StorageForBulk().index('event-reshaping').load(limit=limit)


async def load_by_tag(tag):
    return await StorageFor.crud('event-reshaping', class_type=EventReshapingSchema).load_by('tags', tag)


async def load_by_event_type(event_type: str) -> StorageRecords:
    return await StorageFor.crud('event-reshaping', class_type=EventReshapingSchema).load_by(
        'event_type',
        event_type
    )


async def delete(id: str):
    return await StorageFor(Entity(id=id)).index("event-reshaping").delete()


async def count_by_type(event_type: str) -> int:
    return await storage_manager("event-reshaping").count({"query": {"term": {"event_type": event_type}}})
