import datetime

from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventPayloadMetadata

from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.time import Time

# todo see if it is correct
# def test_event_payload_time_as_first():
#     ep = EventPayload(
#         time=Time(
#             insert="2012-01-01 00:00:00",
#             create="2011-01-01 00:00:00"
#         ),
#         type="text", tags=[1, 2, 3])
#
#     epm = EventPayloadMetadata(
#         time=Time(
#             insert="2002-01-01 00:00:00",
#             create="2001-01-01 00:00:00"
#         )
#     )
#     event = ep.to_event(epm,
#                         source=Entity(id="1"),
#                         session=Session(id="1", metadata=SessionMetadata()),
#                         profile=Entity(id="1"),
#                         has_profile=True
#                         )
#
#     assert event.metadata.time.insert == datetime.datetime(2012, 1, 1, 0, 0)
#     assert event.metadata.time.create == datetime.datetime(2011, 1, 1, 0, 0)


def test_event_payload_time_fallback():
    ep = EventPayload(type="text", tags=[1, 2, 3])

    epm = EventPayloadMetadata(
        time=Time(
            insert="2002-01-01 00:00:00",
            create="2001-01-01 00:00:00"
        )
    )
    event = ep.to_event(epm,
                        source=Entity(id="1"),
                        session=Session(id="1", metadata=SessionMetadata()),
                        profile=Entity(id="1"),
                        has_profile=True
                        )

    assert event.metadata.time.insert != datetime.datetime(2002, 1, 1, 0, 0)  # Must be now - can not be overridden
    assert event.metadata.time.create == datetime.datetime(2001, 1, 1, 0, 0)


def test_event_payload_should_have_tags():
    ep = EventPayload(type="text", tags=[1, 2, 3])

    epm = EventPayloadMetadata(
        time=Time(
            insert="2002-01-01 00:00:00",
            create="2001-01-01 00:00:00"
        )
    )
    event = ep.to_event(epm,
                        source=Entity(id="1"),
                        session=Session(id="1", metadata=SessionMetadata()),
                        profile=Entity(id="1"),
                        has_profile=True
                        )

    assert event.tags.values == ('1', '2', '3')
    assert event.tags.count == 3
