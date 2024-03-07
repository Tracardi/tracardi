from typing import List

from tracardi.config import memory_cache
from tracardi.domain.destination import Destination
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination
from tracardi.service.storage.mysql.service.destination_service import DestinationService
from tracardi.service.decorators.function_memory_cache import async_cache_for

@async_cache_for(memory_cache.event_destination_cache_ttl)
async def load_event_destinations(event_type, source_id) -> List[Destination]:
    ds = DestinationService()
    generator = (await ds.load_event_destinations(event_type, source_id)).map_to_objects(map_to_destination)
    return [item for item in generator]


@async_cache_for(memory_cache.profile_destination_cache_ttl)
async def load_profile_destinations() -> List[Destination]:
    ds = DestinationService()
    generator = (await ds.load_profile_destinations()).map_to_objects(map_to_destination)
    return [item for item in generator]