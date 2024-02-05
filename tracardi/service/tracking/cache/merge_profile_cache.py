from tracardi.context import Context
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.cache.profile_cache import load_profile_cache, save_profile_cache
from tracardi.service.tracking.locking import Lock, async_mutex
from tracardi.service.utils.getters import get_entity_id
from tracardi.domain.profile import Profile
from tracardi.service.merging.profile_merger import merge_profiles

_redis = RedisClient()

def _merge_with_cache_profile(profile: Profile, context: Context) -> Profile:
    # Loads profile form cache and merges it with the current profile

    _cache_profile = load_profile_cache(profile.id, context)

    if not _cache_profile:
        return profile

    return merge_profiles(base_profile=_cache_profile, new_profile=profile)


def merge_with_cache_and_save_profile(profile: Profile, context: Context):
    profile = _merge_with_cache_profile(profile, context)
    return save_profile_cache(profile)


async def lock_merge_with_cache_and_save_profile(profile: Profile, context: Context, lock_name=None):
    profile_key = Lock.get_key(Collection.lock_tracker, "profile", get_entity_id(profile))
    profile_lock = Lock(_redis, profile_key, default_lock_ttl=3)
    async with async_mutex(profile_lock, name=lock_name):
        return merge_with_cache_and_save_profile(profile, context)