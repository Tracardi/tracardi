from typing import List, TypeVar, Union, Set
from tracardi.context import get_context
from tracardi.domain.session import Session
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.driver.elastic import session as session_db
from tracardi.service.tracking.cache.session_cache import save_session_cache

T = TypeVar("T")

async def save_session_to_db(session: Union[Session, List[Session], Set[Session]]):
    await session_db.save(session)


async def save_session_to_db_and_cache(session: Union[Session, List[Session], Set[Session]]):
    context = get_context()
    save_session_cache(session, context)
    await save_session_to_db(session)


async def save_sessions_in_db(sessions: List[Session]) -> BulkInsertResult:
    return await session_db.save_sessions(sessions)


async def delete_session_from_db(session_id: str, index):
    return await session_db.delete_by_id(session_id, index=index)
