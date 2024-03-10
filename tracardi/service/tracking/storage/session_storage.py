from typing import Optional, Union, List, Set

from tracardi.service.license import License
from tracardi.service.tracking.cache.session_cache import load_session_cache, save_session_cache
from tracardi.context import Context, get_context
from tracardi.domain.session import Session
from tracardi.service.storage.driver.elastic import session as session_db

if License.has_license():
    from com_tracardi.dispatchers.pulsar.session_disaptcher import session_dispatch


async def load_session(session_id: str,
                       context: Optional[Context] = None
                       ) -> Optional[Session]:

    if context is None:
        context = get_context()

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

    if context is None:
        context = get_context()

    if License.has_license():
        session_dispatch(sessions, context)
    else:
        await session_db.save(sessions)
        if refresh:
            await session_db.refresh()

    if cache:
        save_session_cache(sessions, context)


async def store_session(sessions: Union[Session, List[Session], Set[Session]],
                       context: Optional[Context] = None,
                       refresh: bool = False,
                       cache: bool = True
                       ):

    """
    Used to store data.
    """

    if context is None:
        context = get_context()

    await session_db.save(sessions)
    if refresh:
        await session_db.refresh()

    if cache:
        save_session_cache(sessions, context)