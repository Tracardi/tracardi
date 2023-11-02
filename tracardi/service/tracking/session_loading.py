from typing import Tuple, Optional

from uuid import uuid4

from tracardi.service.tracking.storage.session_storage import load_session
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import Session
from tracardi.service.utils.getters import get_entity_id


async def load_or_create_session(tracker_payload: TrackerPayload) -> Tuple[Optional[Session], TrackerPayload]:

    session_id = get_entity_id(tracker_payload.session)

    if session_id is None:

        # Artificial session

        # If no session in tracker payload this means that we do not need session.
        # But we may need an artificial session for workflow handling. We create
        # one but will not save it.

        session_id = str(uuid4())

        session = Session.new(id=session_id)

        # Set session to tracker payload

        tracker_payload.force_session(session)

        # TODO remove after 12-2023
        # # Do not save
        #
        # tracker_payload.options.update({
        #     "saveSession": False
        # })

        return session, tracker_payload

    else:

        # Loads session from ES
        session = await load_session(session_id)

        return session, tracker_payload
