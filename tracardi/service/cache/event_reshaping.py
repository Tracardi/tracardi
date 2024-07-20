from typing import List, Optional

from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping
from tracardi.service.storage.mysql.service.event_reshaping_service import EventReshapingService
from tracardi.service.decorators.function_memory_cache import async_cache_for


@async_cache_for(5)
async def load_and_convert_reshaping(event_type) -> Optional[List[EventReshapingSchema]]:
    ers = EventReshapingService()
    reshape_schemas = await ers.load_by_event_type(event_type)
    if reshape_schemas.exists():
        return reshape_schemas.map_to_objects(map_to_event_reshaping)
    return None
