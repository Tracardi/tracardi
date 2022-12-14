from datetime import datetime

import pytest

from tracardi.domain.time_range_query import DatetimePayload, DatePayload


def test_date_payload():
    result = DatetimePayload.create("now")

    assert isinstance(result, DatePayload)

    result = DatetimePayload.create("-30m")
    assert result.absolute.year == datetime.now().year
    assert result.absolute.month == datetime.now().month
    assert result.absolute.date == datetime.now().day

    result = DatetimePayload.create("2023-01-02 00:13:57")
    assert result.absolute.year == 2023
    assert result.absolute.month == 1
    assert result.absolute.date == 2
    assert result.absolute.hour == 0
    assert result.absolute.minute == 13
    assert result.absolute.second == 57
    assert result.absolute.meridiem == 'AM'

    result = DatetimePayload.create("2023-12-02 14:13:57")
    assert result.absolute.year == 2023
    assert result.absolute.month == 12
    assert result.absolute.date == 2
    assert result.absolute.hour == 14
    assert result.absolute.minute == 13
    assert result.absolute.second == 57
    assert result.absolute.meridiem == 'PM'

    with pytest.raises(ValueError):
        result = DatetimePayload.create("2023-12-02 34:13:57")

    with pytest.raises(ValueError):
        result = DatetimePayload.create("sdsad sd ee")