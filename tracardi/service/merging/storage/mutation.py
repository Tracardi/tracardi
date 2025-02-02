from typing import Union, Optional, List, Set

from tracardi.context import get_context, Context
from tracardi.domain.flat_profile import FlatProfile
from tracardi.service.dependency.adapters.big_data_adapter import *
from tracardi.service.tracking.cache.flat_profile_cache import save_flat_profile_cache


async def save_flat_profile(profiles: Union[FlatProfile, List[FlatProfile], Set[FlatProfile]],
                            context: Optional[Context] = None,
                            refresh: bool = False,
                            cache: bool = True) -> None:
    if context is None:
        context = get_context()

    await bd_apm_adapter.save_profiles(profiles, refresh_after_save=refresh)

    if cache:
        save_flat_profile_cache(profiles, context)

async def delete_multiple_profiles(records_to_delete):
    return await bd_apm_adapter.delete_multiple_profiles(records_to_delete)


async def move_profile_events_and_sessions(duplicate_profile_ids: List[str], merged_profile_id: str):
    # Convert to new format. We add 0 as we do not know the counts of events with given profile id
    duplicate_profile_ids = [(id, 0) for id in duplicate_profile_ids]

    await bd_apm_adapter.move_profile_events_and_sessions(duplicate_profile_ids, merged_profile_id)