from datetime import datetime
from uuid import uuid4

from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracking.storage.session_storage import load_session
from tracardi.domain.session import Session

logger = get_logger(__name__)


def _copy_tracker_payload_session_metadata_1(session: Session, insert: Optional[datetime], update: Optional[datetime], create: Optional[datetime]) -> Session:
    if insert:
        session.metadata.time.insert = insert
    if update:
        session.metadata.time.update = update
    if create:
        session.metadata.time.create = create
    return session


def _create_session_1(session_id: Optional[str], profile_id: Optional[str], insert: Optional[datetime], update: Optional[datetime], create: Optional[datetime]) -> Session:
    # Artificial session (Mutates tracker Payload)

    # If no session in tracker payload this means that we do not need session.
    # But we may need an artificial session for workflow handling. We create
    # one but will not save it.

    if session_id is None:
        logger.warning(
            f"Tracker payload delivered with empty session ID. Session created on server side with random ID.")
        session_id = str(uuid4())

    session = Session.new(id=session_id)
    assert (session.operation.new is True)

    session = _copy_tracker_payload_session_metadata_1(session, insert, update, create)

    # Set profile from tracker payload to session
    if profile_id:
        session.profile = Entity(id=profile_id)

    return session


async def load_or_create_session_1(session_id: Optional[str], profile_id: Optional[str], insert, update,
                                   create) -> Session:
    if session_id is None or session_id.strip() == "":
        return _create_session_1(session_id, profile_id, insert, update, create)

    # Loads session from ES
    session = await load_session(session_id)

    if session is None:
        # Creates session with delivered session id
        return _create_session_1(session_id, profile_id, insert, update, create)

    # Only loaded session must have profile.
    if session.profile is None or not session.profile.id:  # If session profile is none then it is corrupted
        # New session created because it is corrupted
        session = _create_session_1(session_id, profile_id, insert, update, create)
        logger.warning(f"Session {session_id} has no profile and is corrupted. "
                       f"New session (ID: {session.id}) created.")

    return session
