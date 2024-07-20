import threading

from time import sleep

import pytest

from tracardi.context import ServerContext, Context
from tracardi.service.storage.redis.driver.redis_client import RedisClient
from tracardi.service.tracking.locking import Lock, BROKE, LOCKED, mutex


def test_mutex_on_error_must_be_unlocked():
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=100)
        with pytest.raises(ValueError):
            with mutex(lock, name="task1") as _lock:
                # Lock should be true because is locked
                assert lock.is_locked() is True
                raise ValueError("test")

        # Should be unlocked if execution fails
        assert lock.is_locked() is False

        with mutex(lock, name="task2") as _lock:
            # Lock should be true because is locked
            assert lock.is_locked() is True

        # Should be unlocked if completed
        assert lock.is_locked() is False

def test_mutex_multithread_lock_break():
    state = []
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=100)
        def task1():
            try:
                with ServerContext(Context(production=False)):

                    with mutex(lock, name="task1") as _lock:
                        # Lock should be true because is locked
                        assert _lock.state == LOCKED
                        sleep(2)
                        print(_lock.get_state())
                        state.append(1)
            except Exception as e:
                print(repr(e))
                raise e

        def task2():
            try:
                with ServerContext(Context(production=False)):
                    assert lock.is_locked()
                    with mutex(lock, name="task2", break_after_time=1) as _lock:
                        assert _lock.is_locked() is True
                        assert _lock.state == BROKE
                        state.append(2)
            except Exception as e:
                print(repr(e))
                raise e

        thread1 = threading.Thread(target=task1)
        thread2 = threading.Thread(target=task2)

        # Start threads
        thread1.start()
        sleep(.2)
        thread2.start()

        # Join threads to wait for them to finish
        thread1.join()
        thread2.join()

    assert state == [2,1]

def test_mutex_multithread_lock_with_waiting():
    state = []
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=3)
        def task1():
            try:
                with ServerContext(Context(production=False)):
                    # Task 1 waits for 1 sec.
                    with mutex(lock, name="task1") as _lock:
                        # Wait for 1 sec. Check if released every .5 sec
                        sleep(1)
                        state.append(1)

            except Exception as e:
                print(repr(e))
                raise e
        def task2():
            try:
                with ServerContext(Context(production=False)):
                    assert lock.is_locked()
                    # Wait for 3 sec. Check if released every .5 sec
                    with mutex(lock, name="task2") as _lock:
                        sleep(1)
                        state.append(2)

            except Exception as e:
                print(repr(e))
                raise e

        thread1 = threading.Thread(target=task1)
        thread2 = threading.Thread(target=task2)

        # Start threads
        thread1.start()
        sleep(.2)
        thread2.start()

        # Join threads to wait for them to finish
        thread1.join()
        thread2.join()

    assert state == [1,2]


def test_mutex_multithread_lock_with_skip():
    state = []
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=1)
        def task1():
            try:
                with ServerContext(Context(production=False)):
                    # Create task 1 locked for 1 sec
                    with mutex(lock, name="task1") as _lock:
                        assert lock.is_locked()
                        sleep(1)
                        state.append(1)

            except Exception as e:
                print(repr(e))
                raise e
        def task2():
            try:
                with ServerContext(Context(production=False)):
                    assert lock.is_locked()

                    # we expect it to fail as it is locked by task1
                    with pytest.raises(BlockingIOError):
                        # Get mutext that fails when locked
                        with mutex(lock, name="task2", raise_error_when_locked=True):
                            state.append(2)

                    # Wait 2 sec (longer then task1 lock which is 1s)
                    sleep(2)

                    # Should not be locked now
                    assert not lock.is_locked()

                    # We should be able to open mutex
                    with mutex(lock, name="task2") as _lock:
                        assert _lock.is_locked()
                        state.append(3)

            except Exception as e:
                print(repr(e))
                raise e

        thread1 = threading.Thread(target=task1)
        thread2 = threading.Thread(target=task2)

        # Start threads
        thread1.start()
        sleep(.2)
        thread2.start()

        # Join threads to wait for them to finish
        thread1.join()
        thread2.join()

    assert state == [1, 3]