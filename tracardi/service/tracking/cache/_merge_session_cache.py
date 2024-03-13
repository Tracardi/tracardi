# from tracardi.context import get_context
# from tracardi.domain.session import Session
# from tracardi.service.merging.session_merger import merge_sessions
# from tracardi.service.storage.redis.cache import RedisCache
# from tracardi.service.storage.redis_client import RedisClient
# from tracardi.service.tracking.storage.session_storage import load_session, save_session
#
# redis_cache = RedisCache(ttl=None)
# _redis = RedisClient()
#
# async def merge_with_cache_and_save_session(session: Session):
#
#     context = get_context()
#
#     _cache_session = await load_session(session.id, context)
#
#     if not _cache_session:
#         return session
#
#     session = merge_sessions(base_session=_cache_session, session=session)
#
#     await save_session(session, context)
