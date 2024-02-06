from typing import Optional
from tracardi.context import get_context, Context
from tracardi.domain.session import Session
from tracardi.domain.storage_record import RecordMetadata
from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor
from tracardi.service.storage.redis.cache import RedisCache
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.cache.prefix import get_cache_prefix

redis_cache = RedisCache(ttl=None)
_redis = RedisClient()


def get_session_key_namespace(session_id: str, context: Context) -> str:
    return f"{Collection.session}{context.context_abrv()}:{get_cache_prefix(session_id[0:2])}:"


def load_session_cache(session_id: str, context: Context):
    key_namespace = get_session_key_namespace(session_id, context)

    if not redis_cache.has(session_id, key_namespace):
        return None

    context, session, changes, session_metadata = redis_cache.get(
        session_id,
        key_namespace)

    session = Session(**session)
    if session_metadata:
        session.set_meta_data(RecordMetadata(**session_metadata))

    return session


def save_session_cache(session: Optional[Session], context: Optional[Context] = None):
    if session:

        if context is None:
            context = get_context()

        index = session.get_meta_data()

        print(f"Caching with session index {index}")

        try:
            if index is None:
                raise ValueError("Empty session index.")

            redis_cache.set(
                session.id,
                (
                    {
                        "production": context.production,
                        "tenant": context.tenant
                    },
                    session.model_dump(mode="json", exclude_defaults=True, exclude={"operation": ...}),
                    None,
                    index.model_dump(mode="json")
                ),
                get_session_key_namespace(session.id, context)
            )
        except ValueError as e:
            print(e)

