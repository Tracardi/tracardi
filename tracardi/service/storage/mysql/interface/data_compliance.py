from typing import Optional, Tuple, List
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.service.cache.cache_tags import DATA_COMPLIANCE_TAG
from tracardi.service.cache_change_tagger.change_tagger import invalidate_cache_on_update
from tracardi.service.storage.mysql.service.event_data_compliance_service import ConsentDataComplianceService
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance

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


async def delete_by_id(data_compliance_id: str) -> Tuple[bool, Optional[EventDataCompliance]]:
    with invalidate_cache_on_update(*DATA_COMPLIANCE_TAG):
        return await cdcs.delete_by_id(data_compliance_id)


async def insert(consent_data_compliance: EventDataCompliance):
    with invalidate_cache_on_update(*DATA_COMPLIANCE_TAG):
        return await cdcs.insert(consent_data_compliance)


async def load_by_event_type(event_type_id: str, enabled_only: bool = True) -> Tuple[List[EventDataCompliance], int]:
    return _records(await cdcs.load_by_event_type(event_type_id, enabled_only))
