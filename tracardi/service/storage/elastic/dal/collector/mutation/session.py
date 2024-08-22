from collections import defaultdict

from typing import List, Dict, TypeVar, Union, Set
from tracardi.context import Context, ServerContext, get_context
from tracardi.domain.session import Session
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.driver.elastic import session as session_db
from tracardi.service.tracking.cache.session_cache import save_session_cache

T = TypeVar("T")


def _split_by_index(entities: List[T]) -> Dict[str, List[T]]:
    entities_by_index = defaultdict(list)
    for entity in entities:
        if entity.has_meta_data():
            entities_by_index[entity.get_meta_data().index].append(entity)
        else:
            entities_by_index['no-metadata'].append(entity)

    return entities_by_index


async def save_session_to_db(session: Union[Session, List[Session], Set[Session]]):
    await session_db.save(session)


async def save_session_to_db_and_cache(session: Union[Session, List[Session], Set[Session]]):
    context = get_context()
    save_session_cache(session, context)
    await save_session_to_db(session)


async def save_sessions_in_db(sessions: List[Session]) -> BulkInsertResult:
    return await session_db.save_sessions(sessions)


async def store_bulk_session(sessions: List[Session], context: Context):
    with ServerContext(context):
        # Group sessions by index and iterate
        for index, sessions in _split_by_index(sessions).items():
            # Save sessions in Elastic
            await session_db.save(sessions)


async def delete_session_from_db(session_id: str, index):
    return await session_db.delete_by_id(session_id, index=index)
