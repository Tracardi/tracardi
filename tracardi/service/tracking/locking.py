import time
import msgpack
import asyncio

from typing import Union, Tuple, Optional

from tracardi.domain.profile import Profile
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis.driver.redis_client import RedisClient
from tracardi.service.storage.elastic.interface.collector.load.profile import load_profile

logger = get_logger(__name__)
_redis = RedisClient()

LOCKED = 0
BROKE = 1
EXPIRED = 2
RELEASED = 3


class Lock:

    def __init__(self, redis, key, default_lock_ttl: float):
        self._redis = redis
        self._key = key
        self._lock_ttl = default_lock_ttl
        self._mutex_name = None
        self._consumers = []

    @property
    def ttl(self):
        return self._lock_ttl

    @property
    def key(self):
        return self._key

    @property
    def state(self):
        try:
            payload = self.get_lock_metadata()
            if not payload:
                return RELEASED

            _, _, state = payload

            return state
        except Exception as e:
            logger.error(str(e))
            self.unlock()
            return RELEASED

    def lock(self, mutex_name: str):
        logger.debug(f"Locking {self.key}")
        self._set_lock_metadata(time.time(), mutex_name, LOCKED)

    def _set_lock_metadata(self, time: float, mutex_name, state: int):
        payload = msgpack.packb((
            time,
            mutex_name,
            state
        ))
        self._redis.set(self._key, payload, ex=self._lock_ttl)

    def delete(self):
        self._redis.delete(self._key)

    def unlock(self):
        logger.debug(f"UnLocking {self.key}")
        self.delete()
        self._mutex_name = None

    def break_in(self):
        self._update_state(BROKE)

    def expire(self):
        self.delete()

    def is_locked(self) -> bool:
        if self._key is None:
            return False
        return self._redis.exists(self._key) != 0

    def get_lock_metadata(self) -> Optional[Tuple[str, str, int]]:
        payload = self._redis.get(self._key)
        if payload:
            return msgpack.unpackb(payload)

        return None

    def get_locked_inside(self) -> Optional[str]:
        try:
            metadata = self.get_lock_metadata()
            if metadata:
                _, locker, _ = metadata
                return locker
        except Exception as e:
            self.unlock()
            logger.error(str(e))
        return None

    @staticmethod
    def get_key(namespace: str, entity: str, id: str):
        return f"{namespace}{entity}:{id}" if id else None

    def _update_state(self, new_state):
        try:
            payload = self._redis.get(self._key)
            if payload:
                lock_time, mutex_name, state = msgpack.unpackb(payload)
                self._set_lock_metadata(lock_time, mutex_name, new_state)
        except Exception as e:
            logger.error(str(e))

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
        return self.state == BROKE

    def is_expired(self) -> bool:
        return self.state == EXPIRED


class _GlobalMutexLock:

    def __init__(self, lock: Lock, name: str, break_after_time: Union[int, float] = None):
        self._name = name
        self._lock: Lock = lock
        self._wait = 0.05
        self._time = time.time()
        self._break_after_time = break_after_time

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
        try:
            metadata = self._lock.get_lock_metadata()
            if metadata:
                lock_time, _, _ = metadata
                return float(lock_time)
        except Exception as e:
            logger.error(str(e))

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
            self._lock.unlock()

        elif self._lock.key:
            self._lock.unlock()


class GlobalMutexLock(_GlobalMutexLock):

    def _keep_locked_for(self) -> 'Lock':

        lock_time = 0.0
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

                logger.debug(
                    f"Suppressing execution of {self._lock.key}. Process {self._lock.get_locked_inside()} is using resource."
                    f"Expires in {self._lock.ttl}s. Waiting no longer then {_time_to_break}s then skipping execution."
                )

                time.sleep(self._wait)

                continue
            break

        self._lock.lock(self._name)

    def __enter__(self) -> Lock:
        if self._lock.key is None:
            return self._lock
        self._keep_locked_for()
        return self._lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit(exc_type)


class AsyncGlobalMutexLock(_GlobalMutexLock):

    async def _keep_locked_for(self) -> 'Lock':

        while True:
            _now = time.time()
            if self._lock.is_locked():  # Key exists, when expires it will be unlocked

                lock_time = self._get_lock_time()

                # Check if there is a time to break the lock
                _broke, _time_to_break = self._check_if_it_is_time(lock_time, grace_period=self._break_after_time)
                if _broke:  # Time is up
                    # We are fed up waiting
                    logger.info(
                        f"Lock {self._lock.key} breaks. Currently locked by (Running process): {self._lock.get_locked_inside()}, Knocking consumer (Waiting process): {self._name}")
                    self._lock.break_in()  # Still locked but break in marked BROKE
                    return self._lock

                logger.info(
                    f"Suppressing execution of {self._lock.key}. Process {self._lock.get_locked_inside()} is using resource."
                    f"Expires in {self._lock.ttl}s. Waiting no longer then {_time_to_break}s then skipping execution."
                )

                await asyncio.sleep(self._wait)

                continue
            break

        self._lock.lock(self._name)

    async def __aenter__(self):
        if self._lock.key is None:
            return self._lock
        await self._keep_locked_for()
        return self._lock

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._exit(exc_type)


class AsyncProfileMutex(_GlobalMutexLock):

    def __init__(self, profile_id: str, name: str, break_after_time: Union[int, float] = None,
                 raise_error_when_locked: bool = False):
        self.profile_id = profile_id
        profile_key = Lock.get_key(Collection.lock_tracker, "profile", profile_id)
        profile_lock = Lock(_redis, profile_key, default_lock_ttl=3)
        if profile_lock.is_locked() and raise_error_when_locked:
            raise BlockingIOError(
                f"Profile {profile_lock.key} is locked. Currently locked by (Running process): "
                f"{profile_lock.get_locked_inside()}, Knocking consumer (Waiting process): {name}")

        super().__init__(profile_lock, name, break_after_time)

    async def _keep_locked_for(self) -> 'Lock':

        while True:
            _now = time.time()
            if self._lock.is_locked():  # Key exists, when expires it will be unlocked

                lock_time = self._get_lock_time()

                # Check if there is a time to break the lock
                _broke, _time_to_break = self._check_if_it_is_time(lock_time, grace_period=self._break_after_time)
                if _broke:  # Time is up
                    # We are fed up waiting
                    logger.info(
                        f"Lock {self._lock.key} breaks. Currently locked by (Running process): {self._lock.get_locked_inside()}, Knocking consumer (Waiting process): {self._name}")
                    self._lock.break_in()  # Still locked but break in marked BROKE
                    return self._lock

                logger.info(
                    f"Suppressing execution of {self._lock.key}. Process {self._lock.get_locked_inside()} is using resource."
                    f"Expires in {self._lock.ttl}s. Waiting no longer then {_time_to_break}s then skipping execution."
                )

                await asyncio.sleep(self._wait)

                continue
            break

        self._lock.lock(self._name)

    async def __aenter__(self) -> Optional[Profile]:
        if self._lock.key is None:
            return await load_profile(self.profile_id)
        await self._keep_locked_for()
        return await load_profile(self.profile_id)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._exit(exc_type)


def mutex(lock: Lock, name: str, break_after_time: Union[int, float] = None, raise_error_when_locked: bool = False):
    if lock.is_locked() and raise_error_when_locked:
        raise BlockingIOError(
            f"Resource {lock.key} is locked. Currently locked by (Running process): {lock.get_locked_inside()}, Knocking consumer (Waiting process): {name}")
    return GlobalMutexLock(lock, name, break_after_time)


def async_mutex(lock: Lock,
                name: str,
                break_after_time: Union[int, float] = None,
                raise_error_when_locked: bool = False):
    if lock.is_locked() and raise_error_when_locked:
        raise BlockingIOError(
            f"Resource {lock.key} is locked. Currently locked by (Running process): {lock.get_locked_inside()}, Knocking consumer (Waiting process): {name}")
    return AsyncGlobalMutexLock(lock, name, break_after_time)


def profile_mutex(profile_id: str,
                  name: str,
                  break_after_time: Union[int, float] = None,
                  raise_error_when_locked: bool = False):
    return AsyncProfileMutex(profile_id, name, break_after_time, raise_error_when_locked)
