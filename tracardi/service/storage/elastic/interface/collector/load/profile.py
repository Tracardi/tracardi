from typing import Optional, List, Tuple

from tracardi.domain.storage_record import RecordMetadata
from tracardi.service.storage.elastic.dal.profile import load_by_primary_ids
from tracardi.service.tracking.cache.profile_cache import load_profile_cache, save_profile_cache
from tracardi.context import Context, get_context
from tracardi.domain.profile import Profile, FlatProfile
from tracardi.service.storage.elastic.dal import profile as profile_db


async def load_profile_by_id(profile_id: str):
    return await profile_db.load_by_id(profile_id)


async def load_profile_by_primary_ids(profile_id_batch, batch):
    # TODO returns raw data
    return await load_by_primary_ids(profile_id_batch, size=batch)


async def load_profile(profile_id: str, context: Optional[Context] = None, fallback_to_db: bool = True) -> Optional[
    Profile]:
    if context is None:
        context = get_context()

    cached_profile = load_profile_cache(profile_id, context)

    if cached_profile is not None and cached_profile.has_meta_data():
        return cached_profile

    if not fallback_to_db:
        return None

    # This load is acceptable
    profile = await profile_db.load_by_id(profile_id)
    save_profile_cache(profile, context)

    return profile


async def load_profiles_to_merge(merge_key_values: List[tuple],
                                 condition: str = 'must',
                                 limit=1000) -> List[Profile]:
    profiles = await profile_db.load_profiles_to_merge(merge_key_values,
                                                       condition,
                                                       limit)
    return [profile.to_entity(Profile) for profile in profiles]


async def load_profile_duplicates_by_ids(profile_ids: List[str]):
    result = await profile_db.load_profile_duplicates(profile_ids)
    profiles = []
    for row in result:
        profiles.append(row.to_entity(Profile))
    return profiles


async def load_duplicated_profiles_with_metadata(profile: Profile, merge_by: Optional[List[Tuple[str, str]]] = None) -> \
        List[Tuple[FlatProfile, Optional[RecordMetadata]]]:
    duplicated_profiles = await profile_db.load_duplicated_profiles(profile, merge_by)

    return [
        (FlatProfile(profile_record), profile_record.get_meta_data())
        for profile_record in duplicated_profiles
    ]


