from typing import Optional

from tracardi.service.tracking.cache.flat_profile_cache import save_flat_profile_cache, load_flat_profile_cache
from tracardi.context import Context, get_context
from tracardi.domain.flat_profile import FlatProfile
from tracardi.service.storage.elastic.interface import profile as profile_db


async def load_flat_profile(profile_id: str, context: Optional[Context] = None, fallback_to_db: bool = True) -> \
Optional[FlatProfile]:
    if context is None:
        context = get_context()

    cached_profile = load_flat_profile_cache(profile_id, context)
    if cached_profile is not None and cached_profile.has_meta_data():
        cached_profile.monitor_changes(True)
        return cached_profile

    if not fallback_to_db:
        return None

    # This load is acceptable
    flat_profile = await profile_db.load_flat_profile_by_id(profile_id)
    save_flat_profile_cache(flat_profile, context)

    # Monitor change in flat profile
    if flat_profile:
        flat_profile.monitor_changes(True)

    return flat_profile
