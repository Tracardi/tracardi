from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_payload_validator import PayloadValidatorRecord, EventPayloadValidator
from tracardi.exceptions.exception import EventValidatorNotFound


async def add_schema(schema: EventPayloadValidator):
    schema = schema.encode().dict()
    return await storage_manager("validation-schema").upsert(schema)


async def del_schema(event_type: str):
    return await storage_manager("validation-schema").delete(event_type)


async def load_schemas(start: int = 0, limit: int = 10):
    return await storage_manager("validation-schema").load_all(start, limit)


async def get_schema(event_type: str) -> EventPayloadValidator:
    result = await storage_manager("validation-schema").load(event_type)
    if result is None:
        raise EventValidatorNotFound(f"There is no validator object for event type: {event_type}")
    return EventPayloadValidator.decode(PayloadValidatorRecord(**result))
