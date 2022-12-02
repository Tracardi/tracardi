from tracardi.domain.event import Event
from tracardi.service.cache_manager import CacheManager
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.tracker_event_props_reshaper import EventPropsReshaper

cache = CacheManager()


async def reshape_event(event: Event, dot: DotAccessor) -> Event:
    if event.metadata.valid:
        reshape_schemas = await cache.event_reshaping(event.type, ttl=15)
        if reshape_schemas:
            resharper = EventPropsReshaper(
                dot=dot,
                event=event,
            )
            return resharper.reshape(schemas=reshape_schemas)
    return event
