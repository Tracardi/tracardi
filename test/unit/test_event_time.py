from tracardi.domain.time import EventTime


def test_event_time():
    empty = {}
    et = EventTime(**empty)
    assert True