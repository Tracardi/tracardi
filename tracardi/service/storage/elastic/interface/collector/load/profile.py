from typing import Optional

from tracardi.service.storage.elastic.interface.collector.load.flat_profile import load_flat_profile
from tracardi.context import Context
from tracardi.domain.profile import Profile


async def load_profile(profile_id: str, context: Optional[Context] = None, fallback_to_db: bool = True) -> Optional[
    Profile]:
    if profile_id is None:
        return None

    flat_profile = await load_flat_profile(profile_id, context, fallback_to_db)
    # TODO EOFP - End of FlatProfile
    if flat_profile:
        profile = flat_profile.as_profile()
    else:
        profile: Optional[Profile] = None

    return profile

