from typing import Optional
from tracardi.context import get_context, Context
from tracardi.domain.profile import Profile
from tracardi.domain.storage_record import RecordMetadata
from tracardi.service.storage.redis.cache import RedisCache
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.tracking.cache.prefix import get_cache_prefix

redis_cache = RedisCache(ttl=None)


def load_profile_cache(profile_id: str, context: Context) -> Optional[Profile]:
    production = context.context_abrv()

    key_namespace = f"{Collection.profile}{production}:{get_cache_prefix(profile_id[0:2])}:"

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
            f"{Collection.profile}{context.context_abrv()}:{get_cache_prefix(profile.id[0:2])}:"
        )
