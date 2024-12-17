from typing import List

from tracardi.config import memory_cache
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.service.decorators.async_cache import AsyncCache
import tracardi.service.storage.mysql.interface.data_compliance as data_compliance_dao

@AsyncCache(memory_cache.data_compliance_cache_ttl,
            allow_null_values=True,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_data_compliance(event_type_id: str) -> List[EventDataCompliance]:
    records, _ = await data_compliance_dao.load_by_event_type(event_type_id, enabled_only=True)
    return records
