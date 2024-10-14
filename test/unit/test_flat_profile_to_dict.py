from tracardi.domain.flat_event import FlatEvent
from tracardi.service.utils.date import now_in_utc


def test_to_dict():
    now = now_in_utc()
    event = FlatEvent({
        "date": now
    })
    as_dict = event.to_dict()
    assert as_dict['date'] == now.strftime('%Y-%m-%d %H:%M:%S')
