from typing import Optional

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