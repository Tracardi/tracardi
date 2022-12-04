import asyncio
import logging
from typing import Optional, List, Dict, Union
from tracardi.domain.entity import Entity
from tracardi.config import redis_config, tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.singleton import Singleton
from tracardi.service.storage.driver import storage
from tracardi.service.storage.redis_client import AsyncRedisClient, RedisClient

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


# # todo try to use this.
# class AsyncProfileTracksSynchronizer:
#     def __init__(self, profile: Optional[Entity], wait=0.1):
#         self.wait = wait
#         self.profile = profile
#         self.redis = AsyncRedisClient()
#         self.hash = "profile-blocker"
#
#     async def __aenter__(self):
#         max_repeats = 10
#         while True:
#             if await self._is_profile_processed() and max_repeats > 0:
#                 logger.info(f"Waiting for profile {self.profile.id} to finish. Repeat {max_repeats}")
#                 await asyncio.sleep(self.wait)
#                 max_repeats -= 1
#             else:
#                 await self._set_profile_process_id()
#                 return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         await self._delete_profile_process_id()
#
#     def _has_profile(self):
#         return self.profile is not None and self.profile.id is not None
#
#     async def _is_profile_processed(self):
#         if self._has_profile():
#             return await self.redis.client.hexists(self.hash, self.profile.id)
#         return False
#
#     async def _delete_profile_process_id(self):
#         if self._has_profile():
#             return await self.redis.client.hdel(self.hash, self.profile.id)
#
#     async def _set_profile_process_id(self):
#         if self._has_profile():
#             return await self.redis.client.hset(self.hash, self.profile.id, '1')


class ProfileTracksSynchronizer:
    def __init__(self, wait=0.1, ttl=10):
        self.wait = wait
        self.ttl = ttl
        self.redis = RedisClient()
        self.hash = "synchronizer"

    def _get_key(self, key: str) -> str:
        return f"{self.hash}:{key}"

    async def wait_for_unlock(self, key: str, seq: Union[str, int] = None):
        while True:
            if self.is_locked(key):
                logger.info(
                    f"Tracker payload - {seq}: Waiting {self.wait}s for profile {key} to finish. Expires in {self.expires_in(key)}s")
                await asyncio.sleep(self.wait)
                continue
            self.unlock_entity(key)
            break

    def expires_in(self, key: str):
        return self.redis.client.ttl(self._get_key(key))

    def is_locked(self, key: str):
        return self.redis.client.exists(self._get_key(key))

    def unlock_entities(self, keys: str):
        for key in keys:
            self.unlock_entity(key)

    def lock_entity(self, key: str):
        key = self._get_key(key)
        result = self.redis.client.set(key, '1', ex=self.ttl)
        if result is True:
            logger.debug(f"Locking key {key} {result}")

    def unlock_entity(self, key: str):
        key = self._get_key(key)
        result = self.redis.client.delete(key)
        logger.debug(f"UnLocking key {key} {result}")


profile_synchronizer = ProfileTracksSynchronizer(
    wait=tracardi.sync_profile_tracks_wait,
    ttl=5
)
