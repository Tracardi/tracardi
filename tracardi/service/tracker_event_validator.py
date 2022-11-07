from tracardi.domain.event import Event
from tracardi.service.event_validator import validate_with_multiple_schemas
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.storage.driver import storage


async def validate_event(event: Event, dot: DotAccessor) -> Event:
    validation_schemas = await storage.driver.event_validation.load_by_event_type(event.type)

    if validation_schemas:
        if validate_with_multiple_schemas(dot, validation_schemas) is False:
            event.metadata.valid = False
    return event
