from typing import List, Optional

from tracardi.config import memory_cache
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.interface import event_reshaping_dao


@AsyncCache(memory_cache.event_reshaping_cache_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            allow_null_values=True,
            return_cache_on_error=True
            )
async def load_and_convert_reshaping(event_type: str) -> Optional[List[EventReshapingSchema]]:
    reshape_schemas, total = await event_reshaping_dao.load_event_reshaping_by_event_type(event_type)
    if reshape_schemas:
        return reshape_schemas
    return None
