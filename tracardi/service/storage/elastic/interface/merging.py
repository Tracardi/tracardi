import asyncio
from typing import List, Tuple, Optional, Set

from tracardi.domain.profile import Profile
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.storage_record import RecordMetadata, StorageRecords
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.service.storage.elastic.interface import raw as raw_db
from tracardi.service.storage.driver.elastic import event as event_db
from tracardi.service.storage.driver.elastic import session as session_db
from tracardi.service.storage.elastic.interface.collector.mutation import profile as mutation_profile_db

logger = get_logger(__name__)
_max_load_chunk = 1000


async def _load_profile_duplicates(profile_ids: Set[str]) -> StorageRecords:
    return await storage_manager('profile').query({
        "size": _max_load_chunk,
        "query": {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "ids": list(profile_ids)
                        }
                    },
                    {
                        "terms": {
                            "id": list(profile_ids)
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {"metadata.time.insert": "asc"}  # todo maybe should be based on updates (but update should always exist)
        ]
    })


async def _load_duplicated_profiles_with_merge_key(merge_by: List[Tuple[str, str]]) -> StorageRecords:
    return await storage_manager('profile').load_by_values(
        merge_by,
        condition='must',
        limit=_max_load_chunk)


async def load_duplicated_profiles(profile_ids: Set[str], merge_by: Optional[List[Tuple[str, str]]] = None) -> List[
    Tuple[FlatProfile, Optional[RecordMetadata]]]:
    if merge_by is None:
        # merge by ids

        duplicated_profiles = await _load_profile_duplicates(profile_ids)
    else:
        # merge by merge keys
        duplicated_profiles = await _load_duplicated_profiles_with_merge_key(merge_by)

    _size_of_ids = len(profile_ids) if profile_ids else 0
    logger.info(
        f"Loaded in memory {len(duplicated_profiles)} from {duplicated_profiles.total}. Size of merged profile IDS: {_size_of_ids}")

    return [
        (FlatProfile(profile_record), profile_record.get_meta_data())
        for profile_record in duplicated_profiles
    ]


async def delete_multiple_profiles(profile_tuples: List[Tuple[str, RecordMetadata]]):
    tasks = [asyncio.create_task(mutation_profile_db.delete_profile(profile_id, metadata.index))
             for profile_id, metadata in profile_tuples]
    return await asyncio.gather(*tasks)


async def move_profile_events_and_sessions(duplicate_profile_ids: Set[str], merged_profile_id: str):
    # Changes ids of old events and sessions to match merged profile
    for old_id in duplicate_profile_ids:
        if old_id != merged_profile_id:
            await raw_db.update_profile_ids('event', old_id, merged_profile_id)
            await event_db.refresh()
            await raw_db.update_profile_ids('session', old_id, merged_profile_id)
            await session_db.refresh()


async def delete_duplicated_profiles(
        profiles_with_metadata: List[Tuple[FlatProfile, Optional[RecordMetadata]]],
        merged_profile_id: str) -> Set[str]:
    # Returns deleted record ids

    records_to_delete: List[Tuple[str, RecordMetadata]] = []

    for profile, metadata in profiles_with_metadata:
        profile_id = profile.get('id', None)
        if profile_id != merged_profile_id:
            records_to_delete.append((profile_id, metadata))

    await delete_multiple_profiles(records_to_delete)

    return set([profile_id for profile_id, _ in records_to_delete])


async def save_merged_flat_profile(flat_profile: FlatProfile):
    # Auto refresh db
    await mutation_profile_db.save_flat_profile(flat_profile, refresh=True)


async def save_marked_for_merge_profiles(flat_profiles: List[FlatProfile]):
    # Convert to profiles
    # TODO EOFP - End of FlatProfile
    profiles = [flat_profile.as_profile() for flat_profile in flat_profiles]
    await mutation_profile_db.save_profiles_in_db(profiles)
