from typing import Optional

from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_payload_validator import EventPayloadValidatorRecord, EventPayloadValidator


async def add_schema(schema: EventPayloadValidator):
    schema = schema.encode().dict()
    return await storage_manager("validation-schema").upsert(schema)


async def del_schema(event_type: str):
    return await storage_manager("validation-schema").delete(event_type)


async def get_schema(event_type: str):
    return await storage_manager("validation-schema").load(event_type)


async def load_schemas(start: int = 0, limit: int = 10):
    return await storage_manager("validation-schema").load_all(start, limit)


async def load_schema(event_type: str) -> Optional[EventPayloadValidator]:
    result = await storage_manager("validation-schema").load(event_type)
    if result is not None:
        return EventPayloadValidator.decode(EventPayloadValidatorRecord(**result))
    return None


async def refresh():
    return await storage_manager('validation-schema').refresh()


async def flush():
    return await storage_manager('validation-schema').flush()
