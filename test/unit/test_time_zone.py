from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from tracardi.service.utils.date import add_utc_time_zone_if_none


def test_returns_none_if_input_is_none():
    # Arrange
    dt = None

    # Act
    result = add_utc_time_zone_if_none(dt)

    # Assert
    assert result is None


def test_returns_same_datetime_object_if_it_already_has_timezone():
    # Arrange
    dt = datetime(2022, 1, 1, tzinfo=ZoneInfo('UTC'))

    # Act
    result = add_utc_time_zone_if_none(dt)

    # Assert
    assert result == dt


def test_adds_utc_timezone_to_naive_datetime_object_and_returns_it():
    # Arrange
    dt = datetime(2022, 1, 1)

    # Act
    result = add_utc_time_zone_if_none(dt)

    # Assert
    assert result == datetime(2022, 1, 1, tzinfo=ZoneInfo('UTC'))


def test_returns_same_datetime_object_if_it_has_timezone_but_no_utc_offset():
    # Arrange
    dt = datetime(2022, 1, 1, tzinfo=ZoneInfo('EST'))

    # Act
    result = add_utc_time_zone_if_none(dt)

    # Assert
    assert result == dt


def test_raises_attribute_error_if_input_is_not_datetime_object():
    # Arrange
    dt = "2022-01-01"

    # Act and Assert
    with pytest.raises(AttributeError):
        add_utc_time_zone_if_none(dt)
