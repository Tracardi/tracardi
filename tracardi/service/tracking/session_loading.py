from datetime import datetime
from uuid import uuid4

from typing import Optional

from tracardi.common.logging.log_handler import get_logger
from tracardi.context import get_context
from tracardi.domain.flat_session import FlatSession

logger = get_logger(__name__)




def _copy_tracker_payload_session_metadata_1(session: FlatSession, insert: Optional[datetime],
                                             update: Optional[datetime], create: Optional[datetime]) -> FlatSession:
    if insert:
        session['metadata.time.insert'] = insert
    if update:
        session['metadata.time.update'] = update
    if create:
        session['metadata.time.create'] = create
    return session


def create_session_1(session_id: Optional[str], insert: Optional[datetime],
                      update: Optional[datetime], create: Optional[datetime]) -> FlatSession:
    # Artificial session (Mutates tracker Payload)

    # If no session in tracker payload this means that we do not need session.
    # But we may need an artificial session for workflow handling. We create
    # one but will not save it.

    if session_id is None:
        logger.warning(
            f"Tracker payload delivered with empty session ID. Session created on server side with random ID.")
        session_id = str(uuid4())

    # Set profile from tracker payload to session
    flat_session = FlatSession.new(id=session_id)
    assert (flat_session.is_new() is True)

    flat_session = _copy_tracker_payload_session_metadata_1(flat_session, insert, update, create)

    return flat_session

