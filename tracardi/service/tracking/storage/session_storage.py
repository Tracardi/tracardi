from typing import Optional, Union, List, Set

from tracardi.service.tracking.cache.session_cache import load_session_cache, save_session_cache
from tracardi.context import get_context
from tracardi.domain.session import Session
from tracardi.service.storage.driver.elastic import session as session_db


async def load_session(session_id: str) -> Optional[Session]:
    cached_session = load_session_cache(session_id, get_context())
    if cached_session is not None:
        return cached_session

    session = await session_db.load_by_id(session_id)
    if session:
        save_session_cache(session)

    return session


async def save_session(sessions: Union[Session, List[Session], Set[Session]]):
    result = await session_db.save(sessions)

    """
    Until the session is saved and it is usually within 1s the system can create many profiles 
    for 1 session.  System checks if the session exists by loading it from ES. If it is a new 
    session then is does not exist and must be saved before it can be read. So there is a 
    1s when system thinks that the session does not exist.

    If session is new we will refresh the session in ES.
    """

    await session_db.refresh()

    return result
