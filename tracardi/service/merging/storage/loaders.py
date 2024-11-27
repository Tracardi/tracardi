from typing import List, Tuple

from tracardi.domain.profile import Profile
from tracardi.service.adapter.bigdata.adapter_selector import bd_apm_adapter

_apm_adapter = bd_apm_adapter()

async def load_duplicated_profiles_with_ids(profile_ids) -> List[Profile]:
    records = await _apm_adapter.load_duplicated_profiles_with_ids(profile_ids)
    profiles = []
    for record in records:
        profiles.append(record.to_entity(Profile))
    return profiles


async def load_duplicated_profiles_with_merge_key(merge_key_values: List[Tuple[str, str]],
                                                  condition: str = 'must',
                                                  limit=1000) -> List[Profile]:

    profiles = await _apm_adapter.load_duplicated_profiles_with_merge_key(merge_key_values,
        condition=condition,
        limit=limit)
    return [profile.to_entity(Profile) for profile in profiles]