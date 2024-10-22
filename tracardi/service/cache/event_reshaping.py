from typing import List, Optional

from tracardi.config import memory_cache
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping
from tracardi.service.storage.mysql.service.event_reshaping_service import EventReshapingService


@AsyncCache(memory_cache.event_reshaping_cache_ttl,
            timeout=.5,
            max_one_cache_fill_every=.1,
            allow_null_values=True,
            return_cache_on_error=True
            )
async def load_and_convert_reshaping(event_type) -> Optional[List[EventReshapingSchema]]:
    ers = EventReshapingService()
    reshape_schemas = await ers.load_by_event_type(event_type)
    if reshape_schemas.exists():
        return reshape_schemas.map_to_objects(map_to_event_reshaping)
    return None
