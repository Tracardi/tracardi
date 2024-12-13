from typing import List

from tracardi.config import memory_cache
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.interface import event_to_profile_dao


@AsyncCache(memory_cache.event_to_profile_coping_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_event_to_profile(event_type_id: str) -> List[EventToProfile]:
    mappings, total = await event_to_profile_dao.load_event_to_profile_mapping_by_type(event_type_id, enabled_only=True)
    if not mappings:
        return []
    return mappings
