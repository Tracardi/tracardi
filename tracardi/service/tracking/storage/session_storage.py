from typing import Optional, Union, List, Set

from tracardi.service.adapter.bigdata.adapter_selector import bd_session_adapter
from tracardi.service.tracking.cache.session_cache import load_session_cache, save_session_cache
from tracardi.context import Context, get_context
from tracardi.domain.session import Session

_bd_session_adapter = bd_session_adapter()

async def load_session(session_id: str,
                       context: Optional[Context] = None
                       ) -> Optional[Session]:
    if context is None:
        context = get_context()

    cached_session = load_session_cache(session_id, context)
    if cached_session is not None:
        return cached_session

    session = await _bd_session_adapter.load_session_from_db(session_id)
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

    await _bd_session_adapter.save_session_to_db(sessions)
    if refresh:
        await _bd_session_adapter.refresh_session_db()

    if cache:
        save_session_cache(sessions, context)
