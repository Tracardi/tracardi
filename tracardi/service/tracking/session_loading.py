from datetime import datetime
from uuid import uuid4

from typing import Tuple, Optional

from tracardi.domain.entity import Entity
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracking.storage.session_storage import load_session
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import Session
from tracardi.service.utils.getters import get_entity_id

logger = get_logger(__name__)


# TODO Remove after 2024-12-01
def _copy_tracker_payload_session_metadata(tracker_payload: TrackerPayload, session: Session) -> Session:
    if tracker_payload.session and tracker_payload.session.metadata:
        if tracker_payload.session.metadata.insert:
            session.metadata.time.insert = tracker_payload.session.metadata.insert
        if tracker_payload.session.metadata.update:
            session.metadata.time.update = tracker_payload.session.metadata.update
        if tracker_payload.session.metadata.create:
            session.metadata.time.create = tracker_payload.session.metadata.create
    return session


# TODO Remove after 2024-12-01
def _create_session(tracker_payload: TrackerPayload) -> Session:
    # Artificial session (Mutates tracker Payload)

    # If no session in tracker payload this means that we do not need session.
    # But we may need an artificial session for workflow handling. We create
    # one but will not save it.

    session_id = tracker_payload.get_session_id()
    if session_id is None:
        logger.warning(
            f"Tracker payload delivered with empty session ID. Session created on server side with random ID.")
        session_id = str(uuid4())

    session = Session.new(id=session_id)
    assert (session.operation.new is True)

    _copy_tracker_payload_session_metadata(tracker_payload, session)

    # Set profile from tracker payload to session
    if isinstance(tracker_payload.profile, Entity) and tracker_payload.profile.id:
        session.profile = Entity(id=tracker_payload.profile.id)

    return session


# TODO Remove after 2024-12-01
# async def load_or_create_session(tracker_payload: TrackerPayload) -> Tuple[Session, TrackerPayload]:
#     session_id = get_entity_id(tracker_payload.session)
#
#     if session_id is None or session_id.strip() == "":
#         session = _create_session(tracker_payload)
#
#     else:
#
#         # Loads session from ES
#         session = await load_session(session_id)
#
#         if session is not None:
#             # Only loaded session must have profile.
#             if session.profile is None or not session.profile.id:  # If session profile is none then it is corrupted
#                 # New session created because it is corrupted
#                 session = _create_session(tracker_payload)
#                 logger.warning(f"Session {session_id} has no profile and is corrupted. "
#                                f"New session (ID: {session.id}) created.")
#
#         else:
#             # Creates session with delivered session id
#             session = _create_session(tracker_payload)
#
#     # AT THIS POINT session should not be empty.
#     # Profile may not be attached if new session.
#
#     # Consistency checks
#
#     if not session:
#         raise AssertionError("No session created.")
#
#     # # TODO Tu konfikt nie jest mozliwy do sprawdzenia (brak profile.ids, profil nie załadowany)
#     # # Załadowana lub stworzona nowa sesja wskazuje na inny profile ID niz profile ID w tracker payload
#     # conflicting_profiles = tracker_payload.profile and session.profile.id != tracker_payload.profile.id
#     # if conflicting_profiles:
#     #     logger.warning(
#     #         f"A loaded session (ID: {session.id}) or newly created session profile ID ({session.profile.id}) points "
#     #         f"to a different profile ID {tracker_payload.profile.id} in the tracker payload. Payload: {orig_tracker_payload}")
#     #     tracker_payload.context.update({
#     #         "session_conflict": {
#     #             "session_id": session_id,
#     #             "profile_in_payload": tracker_payload.profile.id,
#     #             "profile_id_in_loaded_session": session.profile.id
#     #         }
#     #     })
#     #     # Chrońmy te dane i zróbmy nową sesje.
#     #     session = tracker_payload._fill_session_metadata(
#     #         Session.new(
#     #             id=get_shadow_session_id(session_id),
#     #             profile_id=tracker_payload.profile.id))
#     #     session.set_updated(True)
#
#     return session, tracker_payload


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
