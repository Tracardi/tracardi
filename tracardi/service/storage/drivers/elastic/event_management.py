from typing import Optional

from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_payload_validator import EventPayloadValidatorRecord, EventTypeManager


async def add_event_type_metadata(schema: EventTypeManager):
    schema = schema.encode().dict()
    return await storage_manager("event-management").upsert(schema)


async def del_event_type_metadata(event_type: str):
    return await storage_manager("event-management").delete(event_type)


async def get_event_type_metadata(event_type: str):
    return await storage_manager("event-management").load(event_type)


async def load_events_type_metadata(start: int = 0, limit: int = 10):
    return await storage_manager("event-management").load_all(start, limit)


async def load_event_type_metadata(event_type: str) -> Optional[EventTypeManager]:
    result = await storage_manager("event-management").load(event_type)
    if result is not None:
        return EventTypeManager.decode(EventPayloadValidatorRecord(**result))
    return None


async def refresh():
    return await storage_manager('event-management').refresh()


async def flush():
    return await storage_manager('event-management').flush()
