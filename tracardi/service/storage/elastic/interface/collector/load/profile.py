from typing import Optional

from tracardi.service.tracking.cache.profile_cache import load_profile_cache, save_profile_cache
from tracardi.context import Context, get_context
from tracardi.domain.profile import Profile
from tracardi.service.storage.elastic.interface import profile as profile_db


async def load_profile(profile_id: str, context: Optional[Context] = None, fallback_to_db: bool = True) -> Optional[
    Profile]:
    if context is None:
        context = get_context()

    cached_profile = load_profile_cache(profile_id, context)

    if cached_profile is not None and cached_profile.has_meta_data():
        return cached_profile

    if not fallback_to_db:
        return None

    # This load is acceptable
    profile = await profile_db.load_by_id(profile_id)
    save_profile_cache(profile, context)

    return profile

