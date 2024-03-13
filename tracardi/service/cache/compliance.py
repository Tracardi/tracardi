from typing import List

from tracardi.config import memory_cache
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance
from tracardi.service.storage.mysql.service.event_data_compliance_service import ConsentDataComplianceService

@async_cache_for(memory_cache.data_compliance_cache_ttl)
async def load_data_compliance(event_type_id: str) -> List[EventDataCompliance]:
    cdcs = ConsentDataComplianceService()
    records = await cdcs.load_by_event_type(event_type_id, enabled_only=True)
    if not records.exists():
        return []
    return list(records.map_to_objects(map_to_event_data_compliance))