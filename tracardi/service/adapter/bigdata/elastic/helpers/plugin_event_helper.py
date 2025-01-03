from typing import Optional

from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def get_nth_last_event(event_type: str, n: int, profile_id: Optional[str] = None):
    profile_term = {"profile.id": profile_id} if profile_id is not None else {"metadata.profile_less": True}

    result = (await storage_manager("event").query({
        "query": {
            "bool": {
                "must": [
                    {"term": {"type": event_type}},
                    {"term": profile_term}
                ]
            }
        },
        "size": 11,
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    }))

    return result[n] if len(result) >= n + 1 else None


async def load_active_profile_by_field(field: str, value: str, start: int = 0, limit: int = 100) -> StorageRecords:
    query = {
        "from": start,
        "size": limit,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            field: value
                        }
                    },
                    {
                        "term": {
                            "active": True
                        }
                    }
                ]
            }
        }
    }
    return await storage_manager('profile').query(query)
