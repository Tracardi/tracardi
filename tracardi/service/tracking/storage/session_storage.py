from typing import Optional, Union, List, Set

from tracardi.service.tracking.cache.session_cache import load_session_cache, save_session_cache
from tracardi.context import Context
from tracardi.domain.session import Session
from tracardi.service.storage.driver.elastic import session as session_db


async def load_session(session_id: str,
                       context: Optional[Context] = None
                       ) -> Optional[Session]:

    cached_session = load_session_cache(session_id, context)
    if cached_session is not None:
        return cached_session

    session = await session_db.load_by_id(session_id)
    if session:
        save_session_cache(session, context)

    return session


async def save_session(sessions: Union[Session, List[Session], Set[Session]],
                       context: Optional[Context] = None,
                       refresh: bool = False,
                       cache: bool = True
                       ):

    result = await session_db.save(sessions)

    if refresh:
        await session_db.refresh()

    if cache:
        save_session_cache(sessions, context)

    return result
