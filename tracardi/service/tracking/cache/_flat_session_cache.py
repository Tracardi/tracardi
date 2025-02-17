# from typing import Optional, List, Union
#
# from system.adapter.os.bigdata.elastic.model.storage_record import RecordMetadata
# from tracardi.config import tracardi
# from tracardi.context import Context
# from tracardi.domain import ExtraInfo
# from tracardi.domain.session import Session
# from tracardi.common.logging.log_handler import get_logger
# from tracardi.service.storage.redis.collections import Collection
# from tracardi.service.tracking.cache.cache_helper import _get_cache, _has_cache, _delete_cache, _set_cache
# from tracardi.service.tracking.cache.prefix import get_cache_prefix
#
# logger = get_logger(__name__)
#
#
# def get_session_key_namespace(session_id: str, context: Context) -> str:
#     return f"{Collection.session}{context.context_abrv()}:{get_cache_prefix(session_id[0:2])}:"
#
#
# def load_session_cache(session_id: str, context: Context):
#     if tracardi.keep_session_in_cache_for == 0:
#         return None
#
#     key_namespace = get_session_key_namespace(session_id, context)
#
#     if not _has_cache(session_id, key_namespace):
#         return None
#
#     context, session, changes, session_metadata = _get_cache(
#         session_id,
#         key_namespace)
#
#     session = Session(**session)
#     if session_metadata:
#         session.set_meta_data(RecordMetadata(**session_metadata))
#
#     return session
#
#
# def _save_single_session(session, context):
#     index = session.get_meta_data()
#
#     if index is None:
#         logger.warning("Empty session metadata. Index is not set. Cached session removed.",
#                        extra=ExtraInfo.exact(origin="cache", package=__name__))
#         _delete_cache(session.id, get_session_key_namespace(session.id, context))
#     else:
#         _set_cache(
#             session.id,
#             (
#                 {
#                     "production": context.production,
#                     "tenant": context.tenant
#                 },
#                 session.model_dump(mode="json", exclude_defaults=True, exclude={"operation": ...}),
#                 None,
#                 index.model_dump(mode="json")
#             ),
#             get_session_key_namespace(session.id, context),
#             ttl=tracardi.keep_session_in_cache_for
#         )
#
#
# def save_session_cache(session: Union[Optional[Session], List[Session]], context: Context):
#     if session:
#
#         if isinstance(session, Session):
#             _save_single_session(session, context)
#         elif isinstance(session, list):
#             for _session in session:
#                 _save_single_session(_session, context)
#         else:
#             raise ValueError(f"Incorrect session value. Expected Session or list of Sessions. Got {type(session)}")
