from tracardi.context import Context
from tracardi.domain.session import Session
from tracardi.service.merging.session_merger import merge_sessions
from tracardi.service.storage.redis.cache import RedisCache
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.locking import Lock, async_mutex
from tracardi.service.tracking.storage.session_storage import load_session, save_session
from tracardi.service.utils.getters import get_entity_id

redis_cache = RedisCache(ttl=None)
_redis = RedisClient()

async def merge_with_cache_and_save_session(session: Session, context: Context):
    _cache_session = await load_session(session.id, context)

    if not _cache_session:
        return session

    session = merge_sessions(base_session=_cache_session, session=session)

    await save_session(session, context)


async def lock_merge_with_cache_and_save_session(session: Session, context: Context, lock_name=None):
    session_key = Lock.get_key(Collection.lock_tracker, "session", get_entity_id(session))
    session_lock = Lock(_redis, session_key, default_lock_ttl=3)
    async with async_mutex(session_lock, name=lock_name):
        await merge_with_cache_and_save_session(session, context)