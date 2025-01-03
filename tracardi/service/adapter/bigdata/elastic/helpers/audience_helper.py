from typing import List

from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def load_by_primary_ids(profile_ids: List[str], size) -> StorageRecords:
    query = {
        "size": size,
        "query": {
            "terms": {
                "id": profile_ids
            }
        }
    }
    return await storage_manager('profile').query(query)