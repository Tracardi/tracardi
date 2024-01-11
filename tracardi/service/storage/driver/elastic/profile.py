from typing import Union, Tuple

from tracardi.domain.profile import *
from tracardi.config import elastic
from tracardi.domain.storage_record import StorageRecord, StorageRecords
from tracardi.exceptions.exception import DuplicatedRecordException
from tracardi.service.console_log import ConsoleLog
from tracardi.service.storage.driver.elastic import raw as raw_db
from tracardi.service.storage.elastic_storage import ElasticFiledSort
from tracardi.service.storage.factory import storage_manager


async def load_profiles_for_auto_merge() -> StorageRecords:
    query = {
      "query": {
        "exists": {
          "field": "metadata.system.aux.auto_merge"
        }
      }
    }

    return await storage_manager('profile').query(query)

async def load_by_id(profile_id: str) -> Optional[StorageRecord]:
    """
    @throws DuplicatedRecordException
    """

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
        }
    }

    profile_records = await storage_manager('profile').query(query)

    if profile_records.total > 1:
        raise DuplicatedRecordException("Profile {} id duplicated in the database..".format(profile_id))

    if profile_records == 0:
        return None

    return profile_records.first()


def load_by_ids(profile_ids: List[str], batch):
    """
    @throws DuplicatedRecordException
    """

    query = {
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
    }

    return storage_manager('profile').scan(query, batch)


async def load_all(start: int = 0, limit: int = 100, sort: List[Dict[str, Dict]] = None):
    return await storage_manager('profile').load_all(start, limit, sort)


async def load_profile_without_identification(tracker_payload,
                                              is_static=False,
                                              console_log: Optional[ConsoleLog] = None) -> Optional[Profile]:
    """
    Loads current profile. If profile was merged then it loads merged profile.
    @throws DuplicatedRecordException
    """
    if tracker_payload.profile is None:
        return None

    profile_id = tracker_payload.profile.id

    profile_record = await load_by_id(profile_id)

    if profile_record is None:

        # Static profiles can be None as they need to be created if does not exist.
        # Static means the profile id was given in the track payload

        if is_static:
            return Profile(id=tracker_payload.profile.id)

        return None

    profile = Profile.create(profile_record)

    return profile


async def load_profiles_to_merge(merge_key_values: List[tuple],
                                 condition: str='must',
                                 limit=1000) -> List[Profile]:
    profiles = await storage_manager('profile').load_by_values(
        merge_key_values,
        condition=condition,
        limit=limit)
    return [profile.to_entity(Profile) for profile in profiles]


async def save(profile: Union[Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    if isinstance(profile, (list, set)):
        for _profile in profile:
            if isinstance(_profile, Profile):
                _profile.mark_for_update()
    elif isinstance(profile, Profile):
        profile.mark_for_update()
    result = await storage_manager('profile').upsert(profile, exclude={"operation": ...})
    if refresh_after_save or elastic.refresh_profiles_after_save:
        await storage_manager('profile').flush()
    return result


async def save_all(profiles: List[Profile]):
    return await storage_manager("profile").upsert(profiles, exclude={"operation": ...})


async def refresh():
    return await storage_manager('profile').refresh()


async def flush():
    return await storage_manager('profile').flush()


async def delete_by_id(id: str, index: str):
    sm = storage_manager('profile')
    return await sm.delete(id, index)


async def bulk_delete_by_id(ids: List[str]):
    sm = storage_manager('profile')
    return await sm.bulk_delete(ids)


def scan(query: dict = None, batch: int = 1000):
    return storage_manager('profile').scan(query, batch)


def query(query: dict = None):
    return storage_manager('profile').query(query)


async def load_by_query_string(query: str):
    return await storage_manager('profile').load_by_query_string(query)


async def update_by_query(query, conflicts: str = 'proceed', wait_for_completion: bool = False):
    return await storage_manager('profile').update_by_query(
        query=query,
        conflicts=conflicts,
        wait_for_completion=wait_for_completion
    )


async def count(query: dict = None):
    return await storage_manager('profile').count(query)


async def load_profile_by_values(key_value_pairs: List[Tuple[str, str]],
                                 sort_by: Optional[List[ElasticFiledSort]] = None,
                                 limit: int = 20) -> StorageRecords:
    return await raw_db.load_by_key_value_pairs('profile', key_value_pairs, sort_by, limit=limit)


async def load_profiles_by_segments(segments: List[str], condition: str = 'must'):
    """
    Requires all segments
    """
    return await storage_manager('profile').load_by_values(
        field_value_pairs=[('segments', segment) for segment in segments],
        condition=condition
    )


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


async def aggregate_by_field(bucket, aggr_field: str, query: dict = None, bucket_size: int = 100,
                             min_docs_count: int = 1):
    _query = {
        "size": 0,
        "aggs": {
            bucket: {
                "terms": {
                    "field": aggr_field,
                    "size": bucket_size,
                    "min_doc_count": min_docs_count
                }
            }
        }
    }

    if query:
        _query['query'] = query

    return await storage_manager('profile').query(_query)
