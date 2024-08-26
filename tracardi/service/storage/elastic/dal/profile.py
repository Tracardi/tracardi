from typing import List, AsyncGenerator, Any, Optional

from tracardi.domain.profile import Profile
from tracardi.domain.storage_record import StorageRecord, StorageRecords
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.service.storage.elastic.dal import raw as raw_db

logger = get_logger(__name__)


async def refresh():
    return await raw_db.refresh('profile')


async def flush():
    return await raw_db.flush('profile')


async def count(query: dict = None) -> dict:
    return await raw_db.count('profile', query)


async def _load_by_id(profile_id: str) -> Optional[StorageRecord]:
    query = {
        "size": 2,
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "ids": profile_id
                        }
                    },
                    {
                        "term": {
                            "id": profile_id
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {
                "metadata.time.update": {
                    "order": "desc"
                }
            }
        ]
    }

    profile_records = await storage_manager('profile').query(query)

    if profile_records.total <= 0:
        return None

    if profile_records.total > 1:
        logger.warning(
            "Profile {} id duplicated in the database. It will be merged with APM worker.".format(profile_id))

    return profile_records.first()


async def _load_modified_top_profiles(size: int) -> StorageRecords:
    query = {
        "size": size,
        "sort": [
            {
                "metadata.time.update": {
                    "order": "desc"
                }
            }
        ]
    }
    return await storage_manager('profile').query(query)


async def _load_by_primary_ids(profile_ids: List[str], size):
    query = {
        "size": size,
        "query": {
            "terms": {
                "id": profile_ids
            }
        }
    }
    return await storage_manager('profile').query(query)


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


async def profile_count_in_db(query: dict = None) -> dict:
    return await count(query)


async def load_profile_by_primary_ids(profile_id_batch, batch):
    return await _load_by_primary_ids(profile_id_batch, size=batch)


async def load_modified_top_profiles(size):
    result = await _load_modified_top_profiles(size)
    return result.dict()


async def load_profiles_for_auto_merge() -> AsyncGenerator[Profile, Any]:
    query = {
        "query": {
            "exists": {
                "field": "metadata.system.aux.auto_merge"
            }
        }
    }
    async for profile_record in storage_manager('profile').scan(query, batch=1000):
        yield profile_record.to_entity(Profile)


async def get_profiles_by_field_and_value(field: str, email: str) -> AsyncGenerator[Profile, Any]:
    query = {
        "query": {
            "term": {
                field: email
            }
        }
    }
    async for profile_record in storage_manager('profile').scan(query, batch=1000):
        yield profile_record.to_entity(Profile)


async def get_duplicated_profiles_by_field(field):
    query = {
        "size": 0,
        "query": {
            "exists": {
                "field": field
            }
        },
        "aggs": {
            "duplicate_emails": {
                "terms": {
                    "field": field,
                    "min_doc_count": 2,
                    "size": 1000
                }
            },
        }
    }
    result = await storage_manager('profile').query(query)
    for bucket in result.aggregations('duplicate_emails').buckets():
        yield bucket['key'], bucket['doc_count']


async def load_profiles_with_duplicated_ids(log_error=True) -> AsyncGenerator[Profile, Any]:
    query = {
        "size": 0,
        "aggs": {
            "duplicate_ids": {
                "terms": {
                    "field": "ids",
                    "min_doc_count": 2,
                    "size": 1000
                }
            }
        }
    }

    records = await storage_manager('profile').query(query, log_error)

    duplicated_ids = set()
    for data in records.aggregations("duplicate_ids").buckets():
        logger.info(f"Found {data['doc_count']} profiles with the same ID='{data['key']}'")
        duplicated_ids.add(data['key'])

    # Now return only one example of duplicated profile, for further merging.
    # All duplicates will be loaded later.

    if duplicated_ids:
        for duplicated_profile_id in duplicated_ids:
            profile_record = await _load_by_id(duplicated_profile_id)
            yield profile_record.to_entity(Profile)


async def load_profile_duplicates(profile_ids: List[str]) -> List[Profile]:
    query = {
        "size": 10000,
        "query": {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "ids": profile_ids
                        }
                    },
                    {
                        "terms": {
                            "id": profile_ids
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {"metadata.time.insert": "asc"}  # todo maybe should be based on updates (but update should always exist)
        ]
    }
    profiles = []
    for row in await storage_manager('profile').query(query):
        profiles.append(row.to_entity(Profile))
    return profiles


async def load_profiles_to_merge(merge_key_values: List[tuple],
                                 condition: str = 'must',
                                 limit=1000) -> List[Profile]:
    profiles = await storage_manager('profile').load_by_values(
        merge_key_values,
        condition=condition,
        limit=limit)
    return [profile.to_entity(Profile) for profile in profiles]


async def delete_by_id(id: str, index: str):
    sm = storage_manager('profile')
    return await sm.delete(id, index)


async def load_by_id(profile_id: str) -> Optional[Profile]:
    profile_record = await _load_by_id(profile_id)

    profile = None
    if profile_record is not None:
        profile = Profile.create(profile_record)

    return profile


async def count_profile_duplicates(profile_ids: List[str]):
    return await storage_manager('profile').count({
        "query": {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "ids": profile_ids
                        }
                    },
                    {
                        "terms": {
                            "id": profile_ids
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    })
