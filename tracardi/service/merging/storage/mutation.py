from typing import Union, Optional, List, Set

from tracardi.context import get_context, Context
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.profile import Profile
from tracardi.service.adapter.bigdata.adapter_selector import bd_apm_adapter
from tracardi.service.tracking.cache.flat_profile_cache import save_flat_profile_cache

_apm_adapter = bd_apm_adapter()

async def save_flat_profile(profiles: Union[FlatProfile, List[FlatProfile], Set[FlatProfile]],
                            context: Optional[Context] = None,
                            refresh: bool = False,
                            cache: bool = True) -> None:
    if context is None:
        context = get_context()

    await _apm_adapter.save_profiles(profiles, refresh_after_save=refresh)

    if cache:
        save_flat_profile_cache(profiles, context)

async def delete_multiple_profiles(records_to_delete):
    return _apm_adapter.delete_multiple_profiles(records_to_delete)


async def move_profile_events_and_sessions(duplicate_profiles: List[Profile], merged_profile: Profile):
    for old_profile in duplicate_profiles:
        if old_profile.id != merged_profile.id:
            await _apm_adapter.update_profile_id_in('event', old_profile.id, merged_profile.id)
            await _apm_adapter.refresh('event')
            await _apm_adapter.update_profile_id_in('session', old_profile.id, merged_profile.id)
            await _apm_adapter.refresh('session')