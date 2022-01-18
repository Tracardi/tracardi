from typing import Optional

from tracardi.domain.record.value_threshold_record import ValueThresholdRecord
from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.factory import storage_manager


async def load(node_id: str, profile_id: Optional[str] = None) -> Optional[ValueThresholdRecord]:
    if profile_id is not None:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "id": {
                                    "value": node_id
                                }
                            }
                        },
                        {
                            "term": {
                                "profile_id": {
                                    "value": profile_id
                                }
                            }
                        }
                    ]
                }
            }
        }
        result = await storage_manager('value-threshold').query(query)
        result = StorageResult(result)
        result = list(result)
        if len(result) != 1:
            return None
        result = result[0]
    else:
        result = await storage_manager('value-threshold').load(node_id)
        if result is None:
            return None

    return ValueThresholdRecord(**result)


async def save(record: ValueThresholdRecord):
    return await storage_manager('value-threshold').upsert(record.dict())


async def delete(node_id: str, profile_id: Optional[str] = None):
    if profile_id is not None:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "id": {
                                    "value": node_id
                                }
                            }
                        },
                        {
                            "term": {
                                "profile_id": {
                                    "value": profile_id
                                }
                            }
                        }
                    ]
                }
            }
        }
        result = await storage_manager('value-threshold').delete_by_query(query)
    else:
        result = await storage_manager('value-threshold').delete(node_id)

    return result


async def refresh():
    return await storage_manager('value-threshold').refresh()
