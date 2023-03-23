from typing import List, Optional, Dict

from tracardi.domain.identification_point import IdentificationPoint
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import storage_manager


async def load_all(start: int = 0, limit: int = 100, sort: List[Dict[str, Dict]] = None) -> StorageRecords:
    return await storage_manager("identification-point").load_all(start, limit, sort)


async def load_enabled(limit: int = 100) -> StorageRecords:
    return await storage_manager("identification-point").load_by_values([("enabled", True)], limit=limit)


async def load_by_id(id) -> Optional[IdentificationPoint]:
    return IdentificationPoint.create(await storage_manager("identification-point").load(id))


async def load_by_event_type(event_type) -> StorageRecords:
    return await storage_manager('identification-point').load_by_values([('event_type.id', event_type)])


async def delete_by_id(id: str) -> dict:
    sm = storage_manager("identification-point")
    return await sm.delete(id, index=sm.get_single_storage_index())


async def upsert(identification_point: IdentificationPoint) -> BulkInsertResult:
    return await storage_manager('identification-point').upsert(identification_point)


async def refresh():
    return await storage_manager('identification-point').refresh()


async def flush():
    return await storage_manager('identification-point').flush()
