from typing import Optional, List, Union
from tracardi.context import Context
from tracardi.domain.session import Session
from tracardi.domain.storage_record import RecordMetadata
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.redis.cache import RedisCache
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.cache.prefix import get_cache_prefix

redis_cache = RedisCache(ttl=None)
_redis = RedisClient()
logger = get_logger(__name__)

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

def _save_single_session(session, context):
    index = session.get_meta_data()

    if index is None:
        logger.error("Empty session index.")

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

def save_session_cache(session: Union[Optional[Session], List[Session]], context: Context):
    if session:

        if isinstance(session, Session):
            _save_single_session(session, context)
        elif isinstance(session, list):
            for _session in session:
                _save_single_session(_session, context)
        else:
            raise ValueError(f"Incorrect session value. Expected Session or list of Sessions. Got {type(session)}")


