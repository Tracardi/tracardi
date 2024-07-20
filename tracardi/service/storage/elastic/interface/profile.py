from typing import List, AsyncGenerator, Any, Optional

from tracardi.context import get_context
from tracardi.domain.profile import Profile
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.driver.elastic import profile as profile_db
from tracardi.service.storage.elastic.driver.factory import storage_manager

logger = get_logger(__name__)


async def profile_count_in_db(query: dict = None) -> dict:
    return await profile_db.count(query)


async def load_profile_by_primary_ids(profile_id_batch, batch):
    return await profile_db.load_by_primary_ids(profile_id_batch, size=batch)


async def load_modified_top_profiles(size):
    result = await profile_db.load_modified_top_profiles(size)
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
            profile_record = await profile_db.load_by_id(duplicated_profile_id)
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


async def refresh():
    return await storage_manager('profile').refresh()


async def load_by_id(profile_id: str) -> Optional[Profile]:
    profile_record = await profile_db.load_by_id(profile_id)

    profile = None
    if profile_record is not None:
        profile = Profile.create(profile_record)

    return profile
