from typing import Union, List, Set, Optional

from dotty_dict import Dotty

from com_tracardi.storage.starrocks.driver.domain.table import Table
from com_tracardi.storage.starrocks.driver.driver import StarrocksDriver
from tracardi.context import Context, get_context
from tracardi.domain.profile import Profile
from tracardi.service.tracking.cache.profile_cache import save_profile_cache

driver = StarrocksDriver()


async def save_profiles_in_db(profiles: Union[Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    if isinstance(profiles, Profile):
        profiles = [profiles]

    flat_profiles = [Dotty(profile.model_dump(mode='json', exclude={"operation": ...})) for profile in profiles]

    return await driver.insert(Table(table="profile", database='tracardi'), flat_profiles)


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
