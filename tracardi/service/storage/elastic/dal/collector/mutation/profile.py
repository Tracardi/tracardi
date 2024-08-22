from typing import Union, List, Set

from tracardi.domain.profile import Profile
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def save(profile: Union[Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    if isinstance(profile, (list, set)):
        for _profile in profile:
            if isinstance(_profile, Profile):
                _profile.mark_for_update()
    elif isinstance(profile, Profile):
        profile.mark_for_update()
    result = await storage_manager('profile').upsert(profile, exclude={"operation": ...})
    if refresh_after_save:
        await storage_manager('profile').flush()
    return result
