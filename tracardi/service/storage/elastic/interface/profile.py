from typing import Union, List, Set

from tracardi.domain.profile import Profile
from tracardi.service.storage.driver.elastic import profile as profile_db

async def profile_count_in_db(query:dict=None):
    return await profile_db.count(query)


async def save_profiles_in_db(profiles: Union[Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    await profile_db.save(profiles, refresh_after_save)


async def load_profile_by_primary_ids(profile_id_batch, batch):
    await profile_db.load_by_primary_ids(profile_id_batch, size=batch)