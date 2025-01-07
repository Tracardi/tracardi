from typing import List

from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.agg_result import AggResult
from tracardi.service.storage.elastic.driver.factory import storage_manager, StorageForBulk


async def unique_field_value(query, limit) -> AggResult:
    return await StorageForBulk().index('event').uniq_field_value("type", search=query, limit=limit)



async def get_events_by_session(session_id: str, limit: int = 100) -> StorageRecords:
    query = {
        "query": {
            "term": {
                "session.id": session_id
            }
        },
        "size": limit,
        "sort": [
            {
                "metadata.time.insert": {"order": "desc"}
            }
        ]
    }
    return await storage_manager("event").query(query)

async def get_events_by_profile(profile_id: str, limit: int = 100) -> StorageRecords:

    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"profile.id": profile_id}},
                    {"range": {"metadata.time.insert": {"gte": f"now-30d"}}}
                ]
            }
        },
        "size": limit,
        "sort": [
            {
                "metadata.time.insert": {"order": "desc"}
            }
        ]
    }

    return await storage_manager("event").query(query)

async def load_profiles_by_segments(segments: List[str], condition: str = 'must') -> StorageRecords:
    """
    Requires all segments
    """
    return await storage_manager('profile').load_by_values(
        field_value_pairs=[('segments', segment) for segment in segments],
        condition=condition
    )

async def get_events_by_session_and_profile(profile_id: str, session_id: str, limit: int = 100) -> StorageRecords:
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"profile.id": profile_id}},
                    {"term": {"session.id": session_id}}
                ]
            }
        },
        "sort": [
            {
                "metadata.time.insert": {"order": "desc"}
            }
        ],
        "size": limit
    }
    return await storage_manager("event").query(query)