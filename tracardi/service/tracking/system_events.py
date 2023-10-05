from uuid import uuid4

from datetime import datetime, timedelta
from tracardi.config import tracardi
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session

from tracardi.domain.time import Time


def add_system_events(profile: Profile, session: Session, tracker_payload: TrackerPayload) -> TrackerPayload:

    """
    Mutates tracker payload
    """

    if profile and profile.operation.new:
        # Add session created
        tracker_payload.events.append(
            EventPayload(
                id=str(uuid4()),
                type='profile-created',
                time=Time(insert=datetime.utcnow() - timedelta(seconds=3)),
                properties={},
                options={"source_id": tracardi.internal_source}
            )
        )

    if session.is_reopened():
        tracker_payload.events.append(
            EventPayload(
                id=str(uuid4()),
                type='visit-started',
                time=Time(insert=datetime.utcnow() - timedelta(seconds=1)),
                properties={
                    'trigger-event-types': [_ev.type for _ev in tracker_payload.events]
                },
                options={"source_id": tracardi.internal_source}
            )
        )

    if session.operation.new:
        # Add session created event to the registered events
        tracker_payload.events.append(
            EventPayload(
                id=str(uuid4()),
                type='session-opened',
                time=Time(insert=datetime.utcnow() - timedelta(seconds=2)),
                properties={},
                options={"source_id": tracardi.internal_source}
            )
        )

    return tracker_payload
