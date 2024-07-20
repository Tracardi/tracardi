import pytest
from datetime import datetime

from tracardi.service.storage.index import Index


def test_month_partitioning():
    index = Index(multi_index=False, index="tracardi-event", mapping=None, staging=False, static=False, single=False,
                  partitioning="month")
    assert index._multi_index_suffix() == f"{datetime.now().year}-{datetime.now().month}"


def test_year_partitioning():
    def _get_quarter(month):
        if 1 <= month <= 3:
            return 1
        elif 4 <= month <= 6:
            return 2
        elif 7 <= month <= 9:
            return 3
        elif 10 <= month <= 12:
            return 4
        else:
            raise ValueError("Invalid month. Month should be between 1 and 12.")

    index = Index(multi_index=False, index="tracardi-event", mapping=None, staging=False, static=False,
                  single=False, partitioning="quarter")
    assert index._multi_index_suffix() == f"{datetime.now().year}-q{_get_quarter(datetime.now().month)}"


def test_hour_partitioning():
    index = Index(multi_index=False, index="tracardi-event", mapping=None, staging=False, static=False, single=False,
                  partitioning="hour")
    assert index._multi_index_suffix() == f"{datetime.now().year}-{datetime.now().month}{datetime.now().day}{datetime.now().hour}"


def test_minute_partitioning():
    index = Index(multi_index=False, index="tracardi-event", mapping=None, staging=False, static=False, single=False,
                  partitioning="minute")
    assert index._multi_index_suffix() == f"{datetime.now().year}-{datetime.now().month}{datetime.now().day}{datetime.now().hour}{datetime.now().minute}"


def test_invalid_partitioning():
    index = Index(multi_index=False, index="tracardi-event", mapping=None, staging=False, static=False, single=False,
                  partitioning="invalid")
    with pytest.raises(ValueError):
        index._multi_index_suffix()
