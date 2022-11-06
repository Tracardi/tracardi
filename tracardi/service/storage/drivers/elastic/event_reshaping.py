from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_reshaping_schema import EventReshapingSchema, EventReshapingSchemaRecord
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, StorageForBulk
from typing import Optional, Tuple, List


async def refresh():
    return await storage_manager('event-reshaping').refresh()


async def flush():
    return await storage_manager('event-reshaping').flush()


async def upsert(data: EventReshapingSchema):
    return await storage_manager('event-reshaping').upsert(data.encode(), replace_id=True)


async def load(id: str) -> Optional[EventReshapingSchema]:
    result: EventReshapingSchemaRecord = await StorageFor(Entity(id=id)).index("event-reshaping").load(
        EventReshapingSchemaRecord
    )
    if not result:
        return None
    return EventReshapingSchema.decode(result)


async def load_all(limit=100) -> Tuple[List[EventReshapingSchema], int]:
    result = await StorageForBulk().index('event-reshaping').load(limit=limit)
    data = [EventReshapingSchema.decode(EventReshapingSchemaRecord(**r)) for r in result]
    return data, result.total


async def load_by_tag(tag):
    result = await StorageFor.crud('event-reshaping', class_type=EventReshapingSchemaRecord).load_by('tags', tag)
    return [EventReshapingSchema.decode(EventReshapingSchemaRecord(**record)) for record in result]


async def load_by_event_type(event_type: str) -> List[EventReshapingSchema]:
    result = await StorageFor.crud('event-reshaping', class_type=EventReshapingSchemaRecord).load_by(
        'event_type',
        event_type
    )
    return [EventReshapingSchema.decode(EventReshapingSchemaRecord(**record)) for record in result]


async def delete(id: str):
    return await StorageFor(Entity(id=id)).index("event-reshaping").delete()


async def count_by_type(event_type: str) -> int:
    return await storage_manager("event-reshaping").count({"query": {"term": {"event_type": event_type}}})
