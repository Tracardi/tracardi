from typing import Optional, Union, List, Set

from tracardi.service.storage.elastic.interface.collector.load.session import load_session_from_db, refresh_session_db
from tracardi.service.storage.elastic.interface.collector.mutation.session import save_session_to_db
from tracardi.service.tracking.cache.session_cache import load_session_cache, save_session_cache
from tracardi.context import Context, get_context
from tracardi.domain.session import Session


async def load_session(session_id: str,
                       context: Optional[Context] = None
                       ) -> Optional[Session]:
    if context is None:
        context = get_context()

    cached_session = load_session_cache(session_id, context)
    if cached_session is not None:
        return cached_session

    session = await load_session_from_db(session_id)
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

    await save_session_to_db(sessions)
    if refresh:
        await refresh_session_db()

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

    await save_session_to_db(sessions)
    if refresh:
        await refresh_session_db()

    if cache:
        save_session_cache(sessions, context)
