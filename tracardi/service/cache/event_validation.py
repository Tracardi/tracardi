from typing import List

from tracardi.config import memory_cache
from tracardi.domain.event_validator import EventValidator
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.interface import event_validation_dao

@AsyncCache(memory_cache.event_validation_cache_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_event_validation(event_type: str) -> List[EventValidator]:
    records, _ = await event_validation_dao.load_by_event_type(event_type, only_enabled=True)
    return records
