import datetime

from tracardi.process_engine.action.v1.time.day_night.service.day_night_checker import day_night_split, is_day


def test_day_night_split():
    sun_rise, sun_set = day_night_split(datetime.datetime.now(), "52.234980", "21.008490")


def test_is_day():
    result = is_day("52.234980", "21.008490")
    assert isinstance(result, bool)
