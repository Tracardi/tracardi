from typing import Optional
from tracardi.context import get_context, Context
from tracardi.domain.profile import Profile
from tracardi.domain.storage_record import RecordMetadata
from tracardi.service.storage.redis.cache import RedisCache
from tracardi.service.storage.redis.collections import Collection

redis_cache = RedisCache(ttl=None)


def _is_valid_hex(string):
    # Check if the string has exactly 2 characters and they are alphanumeric
    if len(string) == 2 and string.isalnum():
        # Check if both characters are lowercase hexadecimal digits
        return all(char.islower() and char in '0123456789abcdef' for char in string)
    return False


def _get_cache_prefix(string: str) -> str:
    if _is_valid_hex(string):
        return string
    else:
        return '00'


def load_profile_cache(profile_id: str, context: Context) -> Optional[Profile]:

    production = context.context_abrv()

    key_namespace = f"{Collection.profile}{production}:{_get_cache_prefix(profile_id[0:2])}:"

    if not redis_cache.has(profile_id, key_namespace):
        return None

    context, profile, profile_metadata = redis_cache.get(
        profile_id,
        key_namespace
    )

    profile = Profile(**profile)
    if profile_metadata:
        profile.set_meta_data(RecordMetadata(**profile_metadata))

    return profile


def save_profile_cache(profile: Optional[Profile]):
    if profile:
        context = get_context()

        redis_cache.set(
            profile.id,
            (
                {
                    "production": context.production,
                    "tenant": context.tenant
                },
                profile.model_dump(mode="json", exclude_defaults=True),
                profile.get_meta_data().model_dump() if profile.has_meta_data() else None
            ),
            f"{Collection.profile}{context.context_abrv()}:{_get_cache_prefix(profile.id[0:2])}:"
        )
