from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_validator import EventValidator, EventValidatorRecord
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, StorageForBulk
from typing import Optional, Tuple, List


async def refresh():
    return await storage_manager('event-validation').refresh()


async def flush():
    return await storage_manager('event-validation').flush()


async def upsert(validator: EventValidator):
    return await storage_manager("event-validation").upsert(validator.encode(), replace_id=True)


async def load(id: str) -> Optional[EventValidator]:
    result: EventValidatorRecord = await StorageFor(Entity(id=id)).index("event-validation").load(
        EventValidatorRecord
    )
    if not result:
        return None
    return EventValidator.decode(result)


async def load_all(limit=100) -> Tuple[List[EventValidator], int]:
    result = await StorageForBulk().index('event-validation').load(limit=limit)
    data = [EventValidator.decode(EventValidatorRecord(**r)) for r in result]
    return data, result.total


async def load_by_tag(tag):
    result = await StorageFor.crud('event-validation', class_type=EventValidatorRecord).load_by('tags', tag)
    return [EventValidator.decode(EventValidatorRecord(**record)) for record in result]


async def load_by_event_type(event_type: str) -> List[EventValidator]:
    result = await StorageFor.crud('event-validation', class_type=EventValidatorRecord).load_by(
        'event_type',
        event_type
    )
    return [EventValidator.decode(EventValidatorRecord(**record)) for record in result]


async def delete(id: str):
    return await StorageFor(Entity(id=id)).index("event-validation").delete()


async def count_by_type(event_type: str) -> int:
    return await storage_manager("event-validation").count({"query": {"term": {"event_type": event_type}}})
