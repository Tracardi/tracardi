import contextlib
import inspect
import logging
import time
import msgpack
import asyncio

from typing import Union, Tuple, Optional

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

LOCKED = 0
BROKE = 1
EXPIRED = 2
RELEASED = 3

unlock_tolerance = 3


class Lock:

    def __init__(self, redis, key, default_lock_ttl: float):
        self._redis = redis
        self._key = key
        self._lock_ttl = default_lock_ttl + unlock_tolerance
        self._mutex_name = None
        self._consumers = []
        if self.is_locked():
            self._state = LOCKED
        else:
            self._state = RELEASED

    @property
    def ttl(self):
        return self._lock_ttl

    @property
    def key(self):
        return self._key

    @property
    def state(self):
        if not self.is_locked():
            self._set_state(RELEASED)

        return self._state

    def lock(self, mutex_name: str, lock_ttl=None):
        payload = msgpack.packb((
            time.time(),
            mutex_name
        ))
        self._redis.set(self._key, payload, ex=lock_ttl if lock_ttl else self._lock_ttl)
        self._set_state(LOCKED)

    def delete(self):
        self._redis.delete(self._key)

    def unlock(self, mutex_name: str):
        self.delete()
        self._set_state(RELEASED)
        self._mutex_name = None

    def break_in(self):
        self._set_state(BROKE)

    def expire(self):
        self._set_state(EXPIRED)
        self.delete()

    def expires(self):
        return self._lock_ttl

    def is_locked(self) -> bool:
        return self._redis.exists(self._key) != 0

    def get_lock_metadata(self) -> Optional[Tuple[str, str]]:
        payload = self._redis.get(self._key)
        if payload:
            return msgpack.unpackb(payload)
        return None

    def get_locked_inside(self) -> Optional[str]:
        metadata = self.get_lock_metadata()
        if metadata:
            _, locker = metadata
            return locker
        return None

    @staticmethod
    def get_key(namespace: str, entity: str, id: str):
        return f"{namespace}{entity}:{id}" if id else None

    def _set_state(self, state):
        self._state = state

    def get_state(self):
        if self.state == BROKE:
            return 'broke'
        elif self.state == LOCKED:
            return 'locked'
        elif self.state == RELEASED:
            return 'released'
        elif self.state == EXPIRED:
            return 'expired'

    def is_broke(self) -> bool:
        return self._state == BROKE

    def is_expired(self) -> bool:
        return self._state == EXPIRED


class _GlobalMutexLock:

    def __init__(self, lock: Lock, name: str, break_after_time: Union[int, float] = None):
        self._name = name
        self._lock: Lock = lock
        self._wait = 0.05
        self._time = time.time()
        self._break_after_time = break_after_time
        self._auto_open_after_time = self._lock.ttl - unlock_tolerance  # release 3 seconds before

        if self._break_after_time is None:
            self._break_after_time = self._lock.ttl + 10

    @property
    def name(self) -> str:
        return self._name

    def _check_if_it_is_time(self, lock_time, grace_period):
        _now = time.time()
        _time_to_act = lock_time + grace_period - _now
        if _time_to_act < 0:  # Time is up
            # We are fed up waiting
            return True, _time_to_act
        return False, _time_to_act

    def _get_lock_time(self) -> float:
        metadata = self._lock.get_lock_metadata()
        if metadata:
            lock_time, _ = metadata
            return float(lock_time)
        return 0.0

    def _get_locked_inside(self) -> Optional[str]:
        metadata = self._lock.get_locked_inside()
        if metadata:
            _, locker = metadata
            return locker
        return None

    def _exit(self, exc_type):
        if exc_type is not None:
            logger.info(f"Unlocking due to error.")
            self._lock.unlock(self._name)

        elif self._lock.key:
            self._lock.unlock(self._name)
            logger.debug(f"Unlocked in {time.time() - self._time}")




class GlobalMutexLock(_GlobalMutexLock):

    def _keep_locked_for(self) -> 'Lock':

        if self._lock.is_locked():
            lock_time = self._get_lock_time()

        while True:
            _now = time.time()
            if self._lock.is_locked():  # Key exists, when expires it will be unlocked

                # Check if there is a time to break the lock
                _broke, _time_to_break = self._check_if_it_is_time(lock_time, grace_period=self._break_after_time)
                if _broke:  # Time is up
                    # We are fed up waiting
                    logger.info(
                        f"Lock {self._lock.key} breaks. Currently locked by (Running process): {self._lock.get_locked_inside()}, Knocking consumer (Waiting process): {self._name}")
                    self._lock.break_in()  # Still locked but break in marked BROKE
                    return self._lock

                _expire, _time_to_expire = self._check_if_it_is_time(lock_time, grace_period=self._auto_open_after_time)
                if _expire:  # we are approaching the expiration time
                    logger.info(
                        f"Lock {self._lock.key} expires after {self._auto_open_after_time}s. Currently locked by (Running process): {self._lock.get_locked_inside()}, Knocking consumer (Waiting process): {self._name}")
                    self._lock.expire()  # Still locked but break in marked BROKE
                    return self._lock

                logger.debug(
                    f"Suppressing execution of {self._lock.key}. Process {self._lock.get_locked_inside()} is using resource."
                    f"Expires in {self._lock.expires()}s. Waiting no longer then {_time_to_break}s then skipping execution."
                )

                time.sleep(self._wait)

                continue
            break

        self._lock.lock(self._name)

    def __enter__(self) -> Lock:
        self._keep_locked_for()
        return self._lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit(exc_type)

class AsyncGlobalMutexLock(_GlobalMutexLock):

    async def _keep_locked_for(self) -> 'Lock':

        if self._lock.is_locked():
            lock_time = self._get_lock_time()

        while True:
            _now = time.time()
            if self._lock.is_locked():  # Key exists, when expires it will be unlocked

                # Check if there is a time to break the lock
                _broke, _time_to_break = self._check_if_it_is_time(lock_time, grace_period=self._break_after_time)
                if _broke:  # Time is up
                    # We are fed up waiting
                    logger.info(
                        f"Lock {self._lock.key} breaks. Currently locked by (Running process): {self._lock.get_locked_inside()}, Knocking consumer (Waiting process): {self._name}")
                    self._lock.break_in()  # Still locked but break in marked BROKE
                    return self._lock

                _expire, _time_to_expire = self._check_if_it_is_time(lock_time, grace_period=self._auto_open_after_time)
                if _expire:  # we are approaching the expiration time
                    logger.info(
                        f"Lock {self._lock.key} expires after {self._auto_open_after_time}s. Currently locked by (Running process): {self._lock.get_locked_inside()}, Knocking consumer (Waiting process): {self._name}")
                    self._lock.expire()  # Still locked but break in marked BROKE
                    return self._lock

                logger.debug(
                    f"Suppressing execution of {self._lock.key}. Process {self._lock.get_locked_inside()} is using resource."
                    f"Expires in {self._lock.expires()}s. Waiting no longer then {_time_to_break}s then skipping execution."
                )

                await asyncio.sleep(self._wait)

                continue
            break

        self._lock.lock(self._name)

    async def __aenter__(self):
        await self._keep_locked_for()
        return self._lock

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._exit(exc_type)

def mutex(lock: Lock, name: str, break_after_time: Union[int, float] = None, raise_error_when_locked:bool = False):
    if lock.is_locked() and raise_error_when_locked:
        raise BlockingIOError(f"Resource {lock.key} is locked. Currently locked by (Running process): {lock.get_locked_inside()}, Knocking consumer (Waiting process): {name}")
    return GlobalMutexLock(lock, name, break_after_time)

def async_mutex(lock: Lock, name: str, break_after_time: Union[int, float] = None, raise_error_when_locked:bool = False):
    if lock.is_locked() and raise_error_when_locked:
        raise BlockingIOError(f"Resource {lock.key} is locked. Currently locked by (Running process): {lock.get_locked_inside()}, Knocking consumer (Waiting process): {name}")
    return AsyncGlobalMutexLock(lock, name, break_after_time)
