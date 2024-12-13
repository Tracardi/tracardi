from typing import List

from tracardi.config import memory_cache
from tracardi.domain.destination import Destination
from tracardi.service.decorators.async_cache import AsyncCache

import tracardi.service.storage.mysql.interface as mysql


@AsyncCache(memory_cache.event_destination_cache_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_event_destinations(event_type, source_id) -> List[Destination]:
    destination, total = await mysql.destination_dao.load_destinations_for_event_type(event_type, source_id)
    return destination


@AsyncCache(memory_cache.profile_destination_cache_ttl,
            timeout=.5,
            max_one_cache_fill_every=.1,
            return_cache_on_error=True
            )
async def load_profile_destinations() -> List[Destination]:
    destination, total = await mysql.destination_dao.load_destinations_for_profile()
    return destination
