from typing import List, Optional, Dict

from tracardi.domain.consent_field_compliance import ConsentFieldCompliance
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import storage_manager


async def load_all(start: int = 0, limit: int = 100, sort: List[Dict[str, Dict]] = None) -> StorageRecords:
    return await storage_manager("consent-data-compliance").load_all(start, limit, sort)


async def load_by_id(id) -> Optional[ConsentFieldCompliance]:
    return ConsentFieldCompliance.create(await storage_manager("consent-data-compliance").load(id))


async def load_by_event_type(event_type) -> StorageRecords:
    return await storage_manager('consent-data-compliance').load_by_values([('event_type.id', event_type),
                                                                            ('enabled', True)])


async def delete_by_id(id: str) -> dict:
    sm = storage_manager("consent-data-compliance")
    return await sm.delete(id, index=sm.get_single_storage_index())


async def upsert(compliance_setting: ConsentFieldCompliance) -> BulkInsertResult:
    return await storage_manager('consent-data-compliance').upsert(compliance_setting)


async def refresh():
    return await storage_manager('consent-data-compliance').refresh()


async def flush():
    return await storage_manager('consent-data-compliance').flush()
