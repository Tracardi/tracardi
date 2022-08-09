from typing import Optional

from tracardi.domain.record.value_threshold_record import ValueThresholdRecord
from tracardi.service.storage.factory import storage_manager


async def load(id: str) -> Optional[ValueThresholdRecord]:
    result = await storage_manager('value-threshold').load(id)

    if result is None:
        return None

    return ValueThresholdRecord(**result)


async def save(record: ValueThresholdRecord):
    return await storage_manager('value-threshold').upsert(record)


async def delete(id: str):
    return await storage_manager('value-threshold').delete(id)


async def refresh():
    return await storage_manager('value-threshold').refresh()
