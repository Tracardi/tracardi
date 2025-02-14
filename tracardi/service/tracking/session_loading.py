from datetime import datetime
from uuid import uuid4

from typing import Optional

from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.flat_session import FlatSession
from tracardi.service.tracking.storage.session_storage import load_flat_session

logger = get_logger(__name__)


def _copy_tracker_payload_session_metadata_1(session: FlatSession, insert: Optional[datetime], update: Optional[datetime], create: Optional[datetime]) -> FlatSession:
    if insert:
        session['metadata.time.insert'] = insert
    if update:
        session['metadata.time.update'] = update
    if create:
        session['metadata.time.create'] = create
    return session


def _create_session_1(session_id: Optional[str], profile_id: Optional[str], insert: Optional[datetime], update: Optional[datetime], create: Optional[datetime]) -> FlatSession:
    # Artificial session (Mutates tracker Payload)

    # If no session in tracker payload this means that we do not need session.
    # But we may need an artificial session for workflow handling. We create
    # one but will not save it.

    if session_id is None:
        logger.warning(
            f"Tracker payload delivered with empty session ID. Session created on server side with random ID.")
        session_id = str(uuid4())

    # Set profile from tracker payload to session
    flat_session = FlatSession.new(id=session_id, profile_id=profile_id)
    assert (flat_session.is_new() is True)

    flat_session = _copy_tracker_payload_session_metadata_1(flat_session, insert, update, create)

    return flat_session


async def load_or_create_session_1(session_id: Optional[str], profile_id: Optional[str], insert, update,
                                   create) -> FlatSession:
    if session_id is None or session_id.strip() == "":
        return _create_session_1(session_id, profile_id, insert, update, create)

    # Loads session from ES
    flat_session = await load_flat_session(session_id)

    if flat_session is None:
        # Creates session with delivered session id
        return _create_session_1(session_id, profile_id, insert, update, create)

    # Only loaded session must have profile.
    if not flat_session.get('profile.id', None):  # If session profile is none then it is corrupted
        # New session created because it is corrupted
        flat_session = _create_session_1(session_id, profile_id, insert, update, create)
        logger.warning(f"Session {session_id} has no profile and is corrupted. "
                       f"New session (ID: {flat_session.id}) created.")

    return flat_session
