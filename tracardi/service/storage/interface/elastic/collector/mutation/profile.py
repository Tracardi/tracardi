from typing import Union, List, Set, Optional

from tracardi.context import Context, get_context
from tracardi.domain.profile import Profile
from tracardi.service.storage.driver.elastic import profile as profile_db
from tracardi.service.tracking.cache.profile_cache import save_profile_cache


async def save_profiles_in_db(profiles: Union[Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    return await profile_db.save(profiles, refresh_after_save)


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
