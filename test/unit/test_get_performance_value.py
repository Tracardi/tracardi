from tracardi.domain.entity import Entity

from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.process_engine.action.v1.connectors.matomo.send_event.service.page_performance import \
    PerformanceValueGetter
from tracardi.domain.event import Event
from tracardi.domain.event_metadata import EventMetadata, EventTime


def test_should_get_previous_value():
    dot = DotAccessor(event=Event(
        id="test-id",
        metadata=EventMetadata(
            time=EventTime()
        ),
        type="test-type",
        source=Entity(id="@test-source"),
        context={
            "performance": {
                "redirectStart": 10,
                "redirectEnd": 0
            }
        }
    ))

    service = PerformanceValueGetter(dot)

    result = service.get_performance_value("redirectEnd")
    assert result == 10
