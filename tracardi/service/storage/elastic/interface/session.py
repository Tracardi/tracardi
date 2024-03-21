from collections import defaultdict

from typing import List, Dict, TypeVar
from tracardi.context import Context, ServerContext
from tracardi.domain.session import Session
from tracardi.service.storage.driver.elastic import session as session_db

T = TypeVar("T")

def _split_by_index(entities: List[T]) -> Dict[str, List[T]]:
    entities_by_index = defaultdict(list)
    for entity in entities:
        if entity.has_meta_data():
            entities_by_index[entity.get_meta_data().index].append(entity)
        else:
            entities_by_index['no-metadata'].append(entity)

    return entities_by_index

async def store_bulk_session(sessions: List[Session], context: Context):
    with ServerContext(context):
        # Group sessions by index and iterate
        for index, sessions in _split_by_index(sessions).items():
            # Save sessions in Elastic
            await session_db.save(sessions)


async def save_sessions_in_db(sessions: List[Session]):
    return await session_db.save_sessions(sessions)


async def load_session_from_db(session_id: str):
    return await session_db.load_by_id(session_id)


async def save_session_to_db(session: Session):
    await session_db.save(session)

async def load_nth_last_session_for_profile(profile_id: str, offset):
    return await session_db.get_nth_last_session(
                profile_id=profile_id,
                n=offset
            )

async def refresh_session_db():
    await session_db.refresh()


async def flush_session_db():
    await session_db.flush()


async def count_sessions_online_in_db():
    return await session_db.count_online()


async def count_online_sessions_by_location_in_db():
    return await session_db.count_online_by_location()


async def count_sessions_in_db():
    return await session_db.count()


async def delete_session_from_db(session_id:str, index):
    return await session_db.delete_by_id(session_id, index=index)