from typing import Optional, List, Union, Set

from tracardi.config import tracardi
from tracardi.context import get_context, Context
from tracardi.domain import ExtraInfo
from tracardi.domain.storage_record import RecordMetadata
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.redis.cache import RedisCache
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis.driver.redis_client import RedisClient
from tracardi.service.tracking.cache.prefix import get_cache_prefix
from tracardi.domain.flat_profile import FlatProfile

logger = get_logger(__name__)
redis_cache = RedisCache(ttl=tracardi.keep_profile_in_cache_for)
_redis = RedisClient()


def get_flat_profile_key_namespace(profile_id, context):
    return f"{Collection.flat_profile}{context.context_abrv()}:{get_cache_prefix(profile_id[0:2])}:"


def delete_flat_profile_cache(profile_id: str, context: Context):
    key_namespace = get_flat_profile_key_namespace(profile_id, context)
    redis_cache.delete(
        profile_id,
        key_namespace
    )


def load_flat_profile_cache(profile_id: str, context: Context) -> Optional[FlatProfile]:
    if tracardi.keep_profile_in_cache_for == 0:
        return None

    key_namespace = get_flat_profile_key_namespace(profile_id, context)

    if not redis_cache.has(profile_id, key_namespace):
        return None

    _data = redis_cache.get(
        profile_id,
        key_namespace
    )

    try:
        context, flat_profile, profile_changes, profile_metadata = _data
    except Exception:
        return None

    flat_profile = FlatProfile(flat_profile)
    if profile_metadata:
        flat_profile.set_meta_data(RecordMetadata(**profile_metadata))

    return flat_profile


def _save_single_flat_profile(flat_profile: FlatProfile, context: Context):
    key = get_flat_profile_key_namespace(flat_profile.id, context)
    index = flat_profile.get_meta_data()

    if index is None:
        logger.warning("Empty profile metadata. Index is not set. Profile removed from cache.",
                       extra=ExtraInfo.exact(origin="cache", package=__name__))
        redis_cache.delete(flat_profile.id, key)
    else:
        value = (
            {
                "production": context.production,
                "tenant": context.tenant
            },
            flat_profile.dump(),
            None,
            index.model_dump(mode="json")
        )

        redis_cache.set(
            flat_profile.id,
            value,
            key
        )


def save_flat_profile_cache(flat_profile: Union[Optional[FlatProfile], List[FlatProfile], Set[FlatProfile]],
                            context: Optional[Context] = None):

    if flat_profile:

        if context is None:
            context = get_context()

        if isinstance(flat_profile, FlatProfile):
            _save_single_flat_profile(flat_profile, context)
        elif isinstance(flat_profile, (list, set)):
            for _profile in flat_profile:
                _save_single_flat_profile(_profile, context)
        else:
            raise ValueError(f"Incorrect profile value. Expected Profile or list of Profiles. Got {type(profile)}")
