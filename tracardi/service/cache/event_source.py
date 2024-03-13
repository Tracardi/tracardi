from typing import Optional

from tracardi.config import memory_cache
from tracardi.domain.event_source import EventSource
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source
from tracardi.service.storage.mysql.service.event_source_service import EventSourceService
from tracardi.service.decorators.function_memory_cache import async_cache_for


@async_cache_for(memory_cache.source_ttl)
async def load_event_source(source_id) -> Optional[EventSource]:
    ess = EventSourceService()
    return (await ess.load_by_id_in_deployment_mode(source_id)).map_to_object(map_to_event_source)