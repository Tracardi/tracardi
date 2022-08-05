from typing import Union, Optional
from tracardi.domain.profile import Profiles, Profile
from tracardi.service.storage.driver import storage


async def merge(profile: Optional[Profile], override_old_data: bool = True, limit: int = 2000) -> Union[Profiles, None]:
    # Merging, schedule save only if there is an update in flow.
    if profile is not None:  # Profile can be None if profile_less event is processed
        if profile.operation.needs_merging():
            return await profile.merge(storage.driver.profile.load_profiles_to_merge,
                                       override_old_data=True,
                                       limit=limit)
    return None
