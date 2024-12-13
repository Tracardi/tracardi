from typing import List

from tracardi.config import memory_cache
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance
from tracardi.service.storage.mysql.service.event_data_compliance_service import ConsentDataComplianceService


@AsyncCache(memory_cache.data_compliance_cache_ttl,
            allow_null_values=True,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_data_compliance(event_type_id: str) -> List[EventDataCompliance]:
    cdcs = ConsentDataComplianceService()
    records = await cdcs.load_by_event_type(event_type_id, enabled_only=True)
    if not records.exists():
        return []
    return list(records.map_to_objects(map_to_event_data_compliance))
