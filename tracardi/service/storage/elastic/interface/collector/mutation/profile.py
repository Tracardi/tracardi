from typing import Union, List, Set, Optional, Tuple

import asyncio

from tracardi.context import Context, get_context
from tracardi.domain.profile import Profile, FlatProfile
from tracardi.domain.storage_record import RecordMetadata
from tracardi.service.storage.elastic.dal.event import update_profile_event
from tracardi.service.storage.elastic.dal.profile import refresh
from tracardi.service.storage.elastic.dal.session import update_session_profile_ids, refresh as refresh_session
from tracardi.service.storage.elastic.interface.gui.event import refresh_event_db
from tracardi.service.tracking.cache.profile_cache import save_profile_cache, delete_profile_cache
from tracardi.service.storage.elastic.dal import raw as raw_db


async def _delete_multiple_profiles(profile_tuples: List[Tuple[str, RecordMetadata]]):
    tasks = [asyncio.create_task(delete_profile(profile_id, metadata.index))
             for profile_id, metadata in profile_tuples]
    await asyncio.gather(*tasks)


async def _delete_duplicated_profiles(
        profiles_with_metadata: List[Tuple[FlatProfile, Optional[RecordMetadata]]],
        merged_profile_id: str) -> Set[str]:
    # Returns deleted record ids

    records_to_delete: List[Tuple[str, RecordMetadata]] = []

    for profile, metadata in profiles_with_metadata:
        profile_id = profile.get('id', None)
        if profile_id != merged_profile_id:
            records_to_delete.append((profile_id, metadata))

    await _delete_multiple_profiles(records_to_delete)

    return set([profile_id for profile_id, _ in records_to_delete])


async def _move_profile_events_and_sessions(duplicate_profile_ids: Set[str], merged_profile_id: str):
    # Changes ids of old events and sessions to match merged profile
    for old_id in duplicate_profile_ids:
        if old_id != merged_profile_id:
            await update_profile_event(old_id, merged_profile_id)
            await refresh_event_db()
            await update_session_profile_ids(old_id, merged_profile_id)
            await refresh_session()


async def _save(profile: Union[Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    if isinstance(profile, (list, set)):
        for _profile in profile:
            if isinstance(_profile, Profile):
                _profile.mark_for_update()
    elif isinstance(profile, Profile):
        profile.mark_for_update()
    result = await raw_db.upsert_document('profile', profile, exclude={"operation": ...})
    if refresh_after_save:
        await raw_db.flush('profile')
    return result


async def save_profiles_in_db(profiles: Union[Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    return await _save(profiles, refresh_after_save)


async def save_profile_in_db_and_cache(profile: Profile):
    save_profile_cache(profile)
    # Save to database - do not defer
    await save_profiles_in_db(profile, refresh_after_save=True)


async def save_profile(profiles: Union[Profile, List[Profile], Set[Profile]],
                       context: Optional[Context] = None,
                       refresh: bool = False,
                       cache: bool = True) -> None:
    if context is None:
        context = get_context()

    await save_profiles_in_db(profiles, refresh_after_save=refresh)

    if cache:
        save_profile_cache(profiles, context)


async def delete_by_id(id: str, index: str):
    return await raw_db.delete_document_by_id('profile', index, id)


async def delete_profile(id: str,
                         index: str,
                         context: Optional[Context] = None,
                         cache: bool = True):
    if context is None:
        context = get_context()

    result = await delete_by_id(id, index)
    await refresh()
    if cache:
        delete_profile_cache(profile_id=id, context=context)

    return result


async def delete_many_profiles(profile_tuples: List[Tuple[str, RecordMetadata]]):
    await _delete_multiple_profiles(profile_tuples)


async def merge_profile_events_and_sessions(duplicate_profile_ids: Set[str], merged_profile_id: str):
    return await _move_profile_events_and_sessions(duplicate_profile_ids, merged_profile_id)


async def delete_duplicated_profiles(
        profiles_with_metadata: List[Tuple[FlatProfile, Optional[RecordMetadata]]],
        merged_profile_id: str) -> Set[str]:
    return await _delete_duplicated_profiles(profiles_with_metadata, merged_profile_id)


async def save_merged_profile(flat_profile: FlatProfile, metadata: RecordMetadata) -> Profile:
    profile = Profile(**flat_profile)
    profile.set_meta_data(metadata)

    # Auto refresh db
    await save_profile(profile, refresh=True)

    return profile
