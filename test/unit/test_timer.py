from collections import defaultdict

from time import sleep, time
import pytest
from tracardi.common.time.timer import Timer


@pytest.fixture
def timer():
    return Timer()


def test_init(timer):
    assert isinstance(timer.time_db, defaultdict)
    assert len(timer.time_db) == 0


def test_reset_timer(timer):
    key = "test_key"
    before = time()
    timer.reset_timer(key)
    after = time()
    assert before <= timer.time_db[key] <= after


def test_get_time_existing_key(timer):
    key = "test_key"
    current_time = time()
    timer.time_db[key] = current_time
    assert timer.get_time(key) == current_time


def test_get_time_non_existing_key(timer):
    assert timer.get_time("non_existing_key") == 0.0


def test_is_time_over_true(timer):
    key = "test_key"
    timer.reset_timer(key)
    sleep(0.1)  # Sleep for 100 milliseconds
    assert timer.is_time_over(key, 0.05)  # 50 milliseconds


def test_is_time_over_false(timer):
    key = "test_key"
    timer.reset_timer(key)
    assert not timer.is_time_over(key, 1)  # 1 second


def test_is_time_over_non_existing_key(timer):
    assert timer.is_time_over("non_existing_key", 0)


def test_multiple_keys(timer):
    timer.reset_timer("key1")
    sleep(0.05)
    timer.reset_timer("key2")

    assert timer.is_time_over("key1", 0.1) is False
    assert timer.is_time_over("key2", 0.1) is False
    assert timer.is_time_over("key1", 0.01) is True
    assert timer.is_time_over("key2", 0.01) is False


def test_reset_timer_updates_existing_key(timer):
    key = "test_key"
    timer.reset_timer(key)
    first_time = timer.get_time(key)
    sleep(0.1)
    timer.reset_timer(key)
    second_time = timer.get_time(key)
    assert second_time > first_time


def test_reset_timer_sets_time_to_zero(timer):
    assert timer.get_time('key1') == 0.0
    assert timer.get_time('key2') == 0.0

    timer.reset_timer('key1')

    assert timer.get_time('key1') != 0.0  # Timestamp is set
    assert timer.get_time('key2') == 0.0

    sleep(0.1)

    assert timer.is_time_over('key1', 0.01)
    assert timer.is_time_over('key2', 10) is False

    timer.reset_timer('key2')

    assert not timer.is_time_over('key1', 1)
    assert not timer.is_time_over('key2', 1)


def test_first_item_flush(timer):

    timer = Timer(max_timeout=1)

    # Getting the time for the first time.
    # It should be 0 - None
    assert timer.get_time('none') == 0
    # It should be not over
    is_over = timer.is_time_over('none', 2)
    assert is_over is False

    # But now it should have timer set for this key
    timestamp1 = timer.get_time('none')
    assert timestamp1 != 0

    sleep(1.1)

    assert timer.is_time_over('none', 3) is True  # It is over because the timer has set max_timeout=2
    timestamp2 = timer.get_time('none')
    assert timestamp2 == timestamp1


