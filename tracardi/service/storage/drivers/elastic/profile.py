from typing import List, Optional
from tracardi.domain.entity import Entity
from tracardi.config import elastic, tracardi
from tracardi.domain.profile import Profile
from tracardi.domain.storage_record import StorageRecord
from tracardi.exceptions.exception import DuplicatedRecordException
from tracardi.service.storage.factory import StorageFor, storage_manager
from tracardi.service.storage.profile_cacher import ProfileCache


async def load_by_id(id: str) -> Optional[StorageRecord]:
    return await storage_manager("profile").load(id)


async def load_merged_profile(id: str) -> Profile:

    """
    Loads current profile. If profile was merged then it loads merged profile.
    """

    if tracardi.cache_profiles is True:
        profile_cache = ProfileCache()
        if profile_cache.exists(id):
            return profile_cache.get_profile(id)
    try:

        entity = Entity(id=id)
        profile = await StorageFor(entity).index('profile').load(Profile)  # type: Profile
        if profile is not None and profile.metadata.merged_with is not None:
            # Has merged profile
            profile = await load_merged_profile(profile.metadata.merged_with)

        return profile

    except DuplicatedRecordException:

        # Merge duplicated profiles
        _duplicated_profiles = await load_duplicates(id)  # 1st records is the newest
        valid_profile_record = _duplicated_profiles.first() # type: StorageRecord
        profile = valid_profile_record.to_entity(Profile)

        if len(_duplicated_profiles) == 1:
            # If 1 then there is no duplication
            return profile

        # We have duplicated records. Delete all but first profile.
        for _profile_record in _duplicated_profiles[1:]:  # type: StorageRecord
            if _profile_record.has_meta_data():
                await storage_manager('profile').delete(id, index=_profile_record.get_meta_data().index)

        return profile


async def load_profiles_to_merge(merge_key_values: List[tuple], limit=1000) -> List[Profile]:
    profiles = await storage_manager('profile').load_by_values(merge_key_values, limit=limit)
    return [Profile(**profile) for profile in profiles]


async def save(profile: Profile, refresh_after_save=False):

    # todo check if needed
    if tracardi.cache_profiles is not False:
        cache = ProfileCache()
        cache.save_profile(profile)

    result = await StorageFor(profile).index().save()
    if refresh_after_save or elastic.refresh_profiles_after_save:
        await storage_manager('profile').flush()
    return result


async def save_all(profiles: List[Profile]):
    return await storage_manager("profile").upsert(profiles)


async def refresh():
    return await storage_manager('profile').refresh()


async def flush():
    return await storage_manager('profile').flush()


async def delete(id: str):
    return await storage_manager('profile').delete(id)


def scan(query: dict = None):
    return storage_manager('profile').scan(query)


async def count(query: dict = None):
    return await storage_manager('profile').count(query)


async def load_duplicates(id: str):
    return await storage_manager('profile').query({
        "query": {
            "term": {
                "_id": id
            }
        },
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    })


async def load_by_field(field: str, value: str, start: int, limit: 2):
    return await storage_manager('profile').query({
        "from": start,
        "size": limit,
        "query": {
            "term": {
                field: value
            }
        }
    })
