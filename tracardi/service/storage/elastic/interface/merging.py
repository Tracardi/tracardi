import asyncio
from typing import List, Tuple, Optional, Set

from tracardi.domain.profile import FlatProfile, Profile
from tracardi.domain.storage_record import RecordMetadata
from tracardi.service.storage.driver.elastic.profile import load_duplicated_profiles_for_profile
from tracardi.service.storage.driver.elastic.raw import update_profile_ids
from tracardi.service.storage.driver.elastic import event as event_db
from tracardi.service.storage.driver.elastic import session as session_db
from tracardi.service.tracking.storage.profile_storage import save_profile, delete_profile


async def load_duplicated_profiles(profile: Profile) -> List[Tuple[FlatProfile, Optional[RecordMetadata]]]:

    duplicated_profiles = await load_duplicated_profiles_for_profile(profile)

    return [
        (FlatProfile(profile_record), profile_record.get_meta_data())
        for profile_record in duplicated_profiles
    ]


async def delete_multiple_profiles(profile_tuples: List[Tuple[str, RecordMetadata]]):
    tasks = [asyncio.create_task(delete_profile(profile_id, metadata.index))
             for profile_id, metadata in profile_tuples]
    return await asyncio.gather(*tasks)


async def move_profile_events_and_sessions(duplicate_profile_ids: Set[str], merged_profile_id: str):
    # Changes ids of old events and sessions to match merged profile
    for old_id in duplicate_profile_ids:
        if old_id != merged_profile_id:
            await update_profile_ids('event', old_id, merged_profile_id)
            await event_db.refresh()
            await update_profile_ids('session', old_id, merged_profile_id)
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


async def save_merged_profile(flat_profile: FlatProfile, metadata: RecordMetadata) -> Profile:

    profile = Profile(**flat_profile)
    profile.set_meta_data(metadata)

    # Auto refresh db
    await save_profile(profile, refresh=True)

    return profile
