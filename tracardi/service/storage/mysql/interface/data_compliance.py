from typing import Optional, Tuple, List
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.service.storage.mysql.service.event_data_compliance_service import ConsentDataComplianceService
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance
from tracardi.config import memory_cache
from tracardi.common.decorator.async_cache import AsyncCache

cdcs = ConsentDataComplianceService()


def _records(records: SelectResult) -> Tuple[List[EventDataCompliance], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_event_data_compliance)), records.count()


async def load_all(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[EventDataCompliance], int]:
    return _records(await cdcs.load_all(search, limit, offset))


async def load_by_id(data_compliance_id: str) -> Optional[EventDataCompliance]:
    record = await cdcs.load_by_id(data_compliance_id)
    return record.map_to_object(map_to_event_data_compliance)


async def load_by_event_type(event_type_id: str, enabled_only: bool = True) -> Tuple[List[EventDataCompliance], int]:
    return _records(await cdcs.load_by_event_type(event_type_id, enabled_only))


# Cache

@AsyncCache(memory_cache.data_compliance_cache_ttl,
            allow_null_values=True,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_data_compliance(event_type_id: str) -> List[EventDataCompliance]:
    records, _ = await load_by_event_type(event_type_id, enabled_only=True)
    return records


async def delete_by_id(data_compliance_id: str) -> Tuple[bool, Optional[EventDataCompliance]]:
    return await cdcs.delete_by_id(data_compliance_id)


async def insert(consent_data_compliance: EventDataCompliance):
    return await cdcs.insert(consent_data_compliance)
