import logging
import time
import asyncio

from typing import Optional

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class GlobalMutexLock:

    def __init__(self, id: Optional[str], entity: str,
                 namespace,
                 redis,
                 policy="lock",
                 unlock=True,
                 lock_ttl=5,
                 name: str = None):
        self.name = str(name) if name else 'unknown'
        self.unlock = unlock
        self.policy = policy
        self._key = f"{namespace}{entity}:{id}" if id else None
        if self._key:
            self.entity = entity
            self.id = id
            self._redis = redis
            self._lock_ttl = lock_ttl
            self._wait = 0.06
            self._time = time.time()

    async def __aenter__(self):
        if self._key:
            if self.policy == 'lock':
                while True:
                    if self._redis.exists(self._key):
                        logger.warning(
                            f"Execution stopped in {self.name}. "
                            f"Waiting {self._wait}s for lock key {self._key} to get released. "
                            f"Lock is created by {self._redis.get(self._key)}. "
                            f"Expires in {self._redis.ttl(self._key)}s"
                        )
                        await asyncio.sleep(self._wait)
                        continue
                    break
                self._redis.set(self._key, self.name, ex=self._lock_ttl)
                return self
            elif self.policy == 'skip':
                if self._redis.exists(self._key):
                    return True
                self._redis.set(self._key, self.name, ex=self._lock_ttl)
                return False
            else:
                raise ValueError('Unknown policy for GlobalMutexLock.')

        return None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._key and self.unlock:
            self._redis.delete(self._key)
            logger.debug(f"Unlocked in {time.time() - self._time}")

    def __enter__(self):
        if self._key:
            if self.policy == 'lock':
                while True:
                    if self._redis.exists(self._key):
                        logger.warning(
                            f"Execution stopped in {self.name}. "
                            f"Waiting {self._wait}s for lock key {self._key} to get released. "
                            f"Lock is created by {self._redis.get(self._key)}. "
                            f"Expires in {self._redis.ttl(self._key)}s"
                        )
                        time.sleep(self._wait)
                        continue
                    break
                self._redis.set(self._key, "1", ex=self._lock_ttl)
                return self
            elif self.policy == 'skip':
                if self._redis.exists(self._key):
                    return True
                self._redis.set(self._key, "1", ex=self._lock_ttl)
                return False
            else:
                raise ValueError('Unknown policy for GlobalMutexLock.')

        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._key and self.unlock:
            self._redis.delete(self._key)
            logger.debug(f"Unlocked in {time.time() - self._time}")
