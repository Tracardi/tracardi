from typing import Tuple
from uuid import uuid4
from datetime import datetime, timedelta

from tracardi.config import tracardi
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.time import Time
from tracardi.service.license import License, LICENSE

if License.has_service(LICENSE):
    from com_tracardi.config import com_tracardi_settings


def add_system_events(profile: Profile, session: Session, tracker_payload: TrackerPayload) -> Tuple[TrackerPayload, Session]:

    # Visit ended never creates system events.
    if tracker_payload.has_event_type('visit-ended'):
        return tracker_payload, session

    """
    Mutates tracker payload
    """
    async_processing = False
    if License.has_service(LICENSE):
        if com_tracardi_settings.async_processing:
            async_processing = True

    if profile and profile.operation.new:
        # Add session created
        tracker_payload.events.append(
            EventPayload(
                id=str(uuid4()),
                type='profile-created',
                time=Time(insert=datetime.utcnow() - timedelta(seconds=3)),
                properties={},
                options={
                    "source_id": tracardi.internal_source,
                    "async": async_processing
                }
            )
        )

    if session:
        if session.is_reopened():

            # Session can not be reopened with event type visit started.

            session.metadata.status = 'started'
            session.operation.update = True
            tracker_payload.events.append(
                EventPayload(
                    id=str(uuid4()),
                    type='visit-started',
                    time=Time(insert=datetime.utcnow() - timedelta(seconds=1)),
                    properties={
                        'trigger-event-types': [_ev.type for _ev in tracker_payload.events]
                    },
                    options={
                        "source_id": tracardi.internal_source,
                        "async": async_processing
                    }
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
                    options={
                        "source_id": tracardi.internal_source,
                        "async": async_processing
                    }
                )
            )

    return tracker_payload, session
