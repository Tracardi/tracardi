from typing import List
from tracardi.domain.entity import Entity
from tracardi.config import elastic, tracardi
from tracardi.domain.profile import Profile
from tracardi.service.storage.factory import StorageFor, storage_manager, StorageForBulk
from tracardi.service.storage.profile_cacher import ProfileCache


async def load_by_id(id: str) -> Profile:
    profile = Profile(id=id)
    return await StorageFor(profile).index().load()


async def load_merged_profile(id: str) -> Profile:
    """
    Loads current profile. If profile was merged then it loads merged profile.
    """

    if tracardi.cache_profiles is not False:
        profile_cache = ProfileCache()
        if profile_cache.exists(id):
            return profile_cache.get_profile(id)

    entity = Entity(id=id)
    profile = await StorageFor(entity).index('profile').load(Profile)  # type: Profile
    if profile is not None and profile.mergedWith is not None:
        # Has merged profile
        profile = await load_merged_profile(profile.mergedWith)

    return profile


async def load_profiles_to_merge(merge_key_values: List[tuple], limit=1000) -> List[Profile]:
    profiles = await storage_manager('profile').load_by_values(merge_key_values, limit=limit)
    return [Profile(**profile) for profile in profiles]


async def save_profile(profile: Profile):
    if tracardi.cache_profiles is not False:
        cache = ProfileCache()
        cache.save_profile(profile)
    result = await StorageFor(profile).index().save()
    if elastic.refresh_profiles_after_save:
        await storage_manager('profile').flush()
    return result


async def save_profiles(profiles: List[Profile]):
    return await StorageForBulk(profiles).index('profile').save()


async def refresh():
    return await storage_manager('profile').refresh()


async def flush():
    return await storage_manager('profile').flush()
