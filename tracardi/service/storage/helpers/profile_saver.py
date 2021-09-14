from tracardi.config import elastic, tracardi
from tracardi.domain.profile import Profile
from tracardi.service.storage.factory import StorageFor, storage
from tracardi.service.storage.profile_cacher import ProfileCache


async def save_profile(profile: Profile):
    if tracardi.cache_profiles is not False:
        cache = ProfileCache()
        cache.save_profile(profile)
    result = await StorageFor(profile).index().save()
    if elastic.refresh_profiles_after_save:
        await storage('profile').flush()
    return result
