from typing import Union, List, Set, Optional

from tracardi.context import Context, get_context
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.profile import Profile
from tracardi.service.storage.driver.elastic import profile as profile_db
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.service.tracking.cache.flat_profile_cache import save_flat_profile_cache, delete_flat_profile_cache


async def save_profiles_in_db(profiles: Union[FlatProfile, Profile, List[FlatProfile], List[Profile], Set[Profile]],
                              refresh_after_save=False):
    return await profile_db.save(profiles, refresh_after_save)


async def save_flat_profile_in_db_and_cache(flat_profile: FlatProfile):
    save_flat_profile_cache(flat_profile)
    # Save to database - do not defer
    await save_profiles_in_db(flat_profile, refresh_after_save=True)


async def save_flat_profile(profiles: Union[FlatProfile, List[FlatProfile], Set[FlatProfile]],
                            context: Optional[Context] = None,
                            refresh: bool = False,
                            cache: bool = True) -> None:
    if context is None:
        context = get_context()

    await save_profiles_in_db(profiles, refresh_after_save=refresh)

    if cache:
        save_flat_profile_cache(profiles, context)


async def save_profile_in_db_and_cache(profile: Profile):

    flat_profile = FlatProfile(profile.model_dump(mode="json"))
    flat_profile.set_meta_data(profile.get_meta_data())

    save_flat_profile_cache(flat_profile)
    # Save to database - do not defer
    await save_profiles_in_db(flat_profile, refresh_after_save=True)

#
# async def save_profile(profiles: Union[Profile, List[Profile], Set[Profile]],
#                        context: Optional[Context] = None,
#                        refresh: bool = False,
#                        cache: bool = True) -> None:
#     if context is None:
#         context = get_context()
#
#     await save_profiles_in_db(profiles, refresh_after_save=refresh)
#
#     if cache:
#         save_profile_cache(profiles, context)


async def _delete_by_id(id: str, index: str):
    sm = storage_manager('profile')
    return await sm.delete(id, index)


async def delete_profile(id: str,
                         index: str,
                         context: Optional[Context] = None,
                         cache: bool = True):
    if context is None:
        context = get_context()

    result = await _delete_by_id(id, index)
    await profile_db.refresh()
    if cache:
        delete_flat_profile_cache(profile_id=id, context=context)

    return result
