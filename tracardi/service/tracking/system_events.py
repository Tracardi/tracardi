from typing import Tuple
from uuid import uuid4
from datetime import timedelta

from tracardi.config import tracardi
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.time import Time
from tracardi.service.utils.date import now_in_utc


def add_system_events(profile: Profile, session: Session, tracker_payload: TrackerPayload) -> Tuple[TrackerPayload, Session]:

    # Visit ended never creates system events.
    if tracker_payload.has_event_type('visit-ended'):
        return tracker_payload, session

    """
    Mutates tracker payload
    """

    async_processing = True

    _now_utc = now_in_utc()

    if profile and profile.is_new() and not tracker_payload.has_event_type('profile-created'):

        _time = _now_utc- timedelta(seconds=3)
        # Add session created
        tracker_payload.events.append(
            EventPayload(
                id=str(uuid4()),
                type='profile-created',
                time=Time(
                    create=_time,
                    insert=_time
                ),
                properties={},
                options={
                    "source_id": tracardi.internal_source,
                    "async": async_processing
                }
            )
        )

    if session:

        if tracker_payload.is_on('saveSession', default=True):

            if session.is_reopened():

                # Session can not be reopened with event type visit started.

                session.metadata.status = 'started'
                session.set_updated()
                _time = _now_utc - timedelta(seconds=1)
                tracker_payload.events.append(
                    EventPayload(
                        id=str(uuid4()),
                        type='visit-started',
                        time=Time(
                            create=_time,
                            insert=_time
                        ),
                        properties={
                            'trigger-event-types': [_ev.type for _ev in tracker_payload.events]
                        },
                        options={
                            "source_id": tracardi.internal_source,
                            "async": async_processing
                        }
                    )
                )

            if session.is_new():
                # Add session created event to the registered events
                _time = _now_utc - timedelta(seconds=2)
                tracker_payload.events.append(
                    EventPayload(
                        id=str(uuid4()),
                        type='session-opened',
                        time=Time(
                            create=_time,
                            insert=_time,
                        ),
                        properties={},
                        options={
                            "source_id": tracardi.internal_source,
                            "async": async_processing
                        }
                    )
                )

    return tracker_payload, session
