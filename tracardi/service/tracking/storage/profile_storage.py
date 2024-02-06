from typing import Optional, Union, List, Set
from tracardi.service.tracking.cache.profile_cache import load_profile_cache, save_profile_cache, delete_profile_cache
from tracardi.context import Context
from tracardi.domain.profile import Profile
from tracardi.service.storage.driver.elastic import profile as profile_db


async def delete_profile(id: str,
                         index: str,
                         context: Optional[Context] = None,
                         cache: bool = True):
    result = await profile_db.delete_by_id(id, index)
    await profile_db.refresh()
    if cache:
        delete_profile_cache(profile_id=id, context=context)

    return result


async def save_profile(profiles: Union[Profile, List[Profile], Set[Profile]],
                       context: Optional[Context] = None,
                       refresh: bool=False,
                       cache: bool = True):

    result = await profile_db.save(profiles,  refresh_after_save=refresh)
    if cache:
        save_profile_cache(profiles, context)
    return result


async def load_profile(profile_id: str, context: Optional[Context] = None, fallback_to_db: bool =True) -> Optional[Profile]:
    cached_profile = load_profile_cache(profile_id, context)

    if cached_profile is not None and cached_profile.has_meta_data():
        return cached_profile

    if not fallback_to_db:
        return None

    # This load is acceptable
    profile_record = await profile_db.load_by_id(profile_id)

    profile = None
    if profile_record is not None:
        profile = Profile.create(profile_record)

    save_profile_cache(profile)

    return profile
