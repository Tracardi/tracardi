from typing import Optional, Union, List, Set
from tracardi.service.tracking.cache.profile_cache import load_profile_cache, save_profile_cache
from tracardi.context import get_context
from tracardi.domain.profile import Profile
from tracardi.service.storage.driver.elastic import profile as profile_db


async def save_profile(profiles: Union[Profile, List[Profile], Set[Profile]]):
    result = await profile_db.save(profiles)
    await profile_db.refresh()

    return result


async def load_profile(profile_id: str) -> Optional[Profile]:
    cached_profile = load_profile_cache(profile_id, context=get_context())

    if cached_profile is not None and cached_profile.has_meta_data():
        return cached_profile

    profile_record = await profile_db.load_by_id(profile_id)

    profile = None
    if profile_record is not None:
        profile = Profile.create(profile_record)

    save_profile_cache(profile)

    return profile
