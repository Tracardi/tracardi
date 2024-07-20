from typing import Tuple

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracking.storage.session_storage import load_session
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import Session
from tracardi.service.utils.getters import get_entity_id

logger = get_logger(__name__)


async def load_or_create_session(tracker_payload: TrackerPayload) -> Tuple[Session, TrackerPayload]:
    session_id = get_entity_id(tracker_payload.session)
    # orig_tracker_payload = tracker_payload.model_dump(mode='json')

    if session_id is None or session_id.strip() == "":

        # Set session to tracker payload. New id created as there is none in session_id
        session = tracker_payload.create_session()

    else:

        # Loads session from ES
        session = await load_session(session_id)

        if session is not None:
            # Only loaded session must have profile.
            if session.profile is None or not session.profile.id:  # If session profile is none then it is corrupted
                session = tracker_payload.create_session()
                logger.warning(f"Session {session_id} has no profile and is corrupted. "
                               f"New session (ID: {session.id}) created.")

        else:
            # Creates session with delivered session id
            session = tracker_payload.create_session()

    # AT THIS POINT session should not be empty.
    # Profile may not be attached if new session.

    # Consistency checks

    if not session:
        raise AssertionError("No session created.")

    # # TODO Tu konfikt nie jest mozliwy do sprawdzenia (brak profile.ids, profil nie załadowany)
    # # Załadowana lub stworzona nowa sesja wskazuje na inny profile ID niz profile ID w tracker payload
    # conflicting_profiles = tracker_payload.profile and session.profile.id != tracker_payload.profile.id
    # if conflicting_profiles:
    #     logger.warning(
    #         f"A loaded session (ID: {session.id}) or newly created session profile ID ({session.profile.id}) points "
    #         f"to a different profile ID {tracker_payload.profile.id} in the tracker payload. Payload: {orig_tracker_payload}")
    #     tracker_payload.context.update({
    #         "session_conflict": {
    #             "session_id": session_id,
    #             "profile_in_payload": tracker_payload.profile.id,
    #             "profile_id_in_loaded_session": session.profile.id
    #         }
    #     })
    #     # Chrońmy te dane i zróbmy nową sesje.
    #     session = tracker_payload._fill_session_metadata(
    #         Session.new(
    #             id=get_shadow_session_id(session_id),
    #             profile_id=tracker_payload.profile.id))
    #     session.set_updated(True)

    return session, tracker_payload
