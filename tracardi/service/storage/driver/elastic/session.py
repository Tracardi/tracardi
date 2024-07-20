from typing import Optional, List, Union, Set

from tracardi.domain.session import Session
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.storage_record import StorageRecord
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.elastic.driver.factory import storage_manager

logger = get_logger(__name__)


async def save_sessions(sessions: List[Session]) -> BulkInsertResult:
    return await storage_manager("session").upsert(sessions, exclude={"operation": ...})


async def save(session: Union[Session, List[Session], Set[Session]]) -> BulkInsertResult:
    return await storage_manager('session').upsert(session, exclude={"operation": ...})


async def exist(id: str) -> bool:
    return await storage_manager("session").exists(id)


async def load_by_id(id: str) -> Optional[Session]:
    session_record = await storage_manager("session").load(id)
    if session_record is None:
        return None

    session = session_record.to_entity(Session)  # 10rq/s

    return session


async def load_duplicates(id: str):
    return await storage_manager('session').query({
        "query": {
            "term": {
                '_id': id
            }
        },
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    })


async def delete_by_id(id: str, index: str):
    sm = storage_manager('session')
    return await sm.delete(id, index)


async def refresh():
    return await storage_manager('session').refresh()


async def flush():
    return await storage_manager('session').flush()


async def get_nth_last_session(profile_id: str, n: int) -> Optional[StorageRecord]:
    query = {
        "query": {
            "term": {"profile.id": profile_id}
        },
        "size": 11,
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    }

    records = await storage_manager('session').query(query)

    record = records.row(n)
    if record is None:
        return None

    return StorageRecord.build_from_elastic(record)


async def count(query: dict = None):
    return await storage_manager('session').count(query)


async def _aggregate_session(bucket_name, by, filter_query=None, buckets_size=100) -> StorageAggregateResult:
    aggregate_query = {
        bucket_name: {
            "terms": {
                "field": by,
                "size": buckets_size,
            }
        }
    }

    if filter_query is None:
        filter_query = {
            "match_all": {}
        }

    query = {
        "size": 0,
        "query": filter_query,
        "aggs": aggregate_query
    }

    return await storage_manager(index="session").aggregate(query)


async def count_online():

    # Count except cardio event source

    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "metadata.time.insert": {
                                "gt": "now-15m"
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "sessions": {
                "cardinality": {
                    "field": "session.id",
                    "precision_threshold": 100
                }
            }
        }
    }

    return await storage_manager('event').query(query)


async def count_online_by_location():
    query = {
        "size": 0,
        "query": {
            "range": {
                "metadata.time.insert": {
                    "gt": "now-15m"
                }
            }
        },
        "aggs": {
            "tz": {
                "terms": {
                    "size": 3,
                    "field": "session.tz"
                }
            }
        }
    }

    return await storage_manager('event').query(query)
