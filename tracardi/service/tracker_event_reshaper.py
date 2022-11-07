from tracardi.domain.event import Event
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.storage.driver import storage
from tracardi.service.tracker_event_props_reshaper import EventPropsReshaper


async def reshape_event(event: Event, dot: DotAccessor) -> Event:
    if event.metadata.valid:
        reshape_schemas = await storage.driver.event_reshaping.load_by_event_type(event.type)
        if reshape_schemas:
            resharper = EventPropsReshaper(
                dot=dot,
                event=event,
            )
            reshape_schemas_objects = reshape_schemas.to_domain_objects(EventReshapingSchema)
            return resharper.reshape(schemas=reshape_schemas_objects)
    return event
