from typing import Optional

from tracardi.config import memory_cache
from tracardi.domain.event_source import EventSource
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.interface import event_source_dao


@AsyncCache(memory_cache.source_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_event_source_via_cache(source_id) -> Optional[EventSource]:
    return await event_source_dao.load_event_source_by_id(source_id)
