# from tracardi.service.storage.redis.collections import Collection
# from tracardi.service.storage.redis_client import RedisClient
# from tracardi.service.tracking.locking import Lock, async_mutex
# from tracardi.service.tracking.storage.profile_storage import load_profile, save_profile
# from tracardi.service.utils.getters import get_entity_id
# from tracardi.domain.profile import Profile
# from tracardi.service.merging.profile_merger import merge_profiles
#
# _redis = RedisClient()
#
#
# # async def merge_with_cache_and_save_profile(profile: Profile):
# #     # Loads profile form cache and merges it with the current profile
# #
# #     _cache_profile = await load_profile(profile.id)
# #
# #     if not _cache_profile:
# #         return profile
# #
# #     profile = merge_profiles(base_profile=_cache_profile, new_profile=profile)
# #
# #     return await save_profile(profile)
#
#
# # async def lock_merge_with_cache_and_save_profile(profile: Profile, lock_name=None):
# #     profile_key = Lock.get_key(Collection.lock_tracker, "profile", get_entity_id(profile))
# #     profile_lock = Lock(_redis, profile_key, default_lock_ttl=3)
# #     async with async_mutex(profile_lock, name=lock_name):
# #         return await merge_with_cache_and_save_profile(profile)
