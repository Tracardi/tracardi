import asyncio
import logging
from typing import Optional, List
from tracardi.domain.entity import Entity
from tracardi.config import redis_config, tracardi
from tracardi.exceptions.log_handler import log_handler
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
    def __init__(self, wait=0.1, max_repeats=20):
        self.wait = wait
        self.entity_id = None
        self.redis = RedisClient()
        self.hash = "ProfileTracksSynchronizer"
        self.max_repeats = max_repeats
        self.locked_entities: List[str] = []
        self.locked_entities_counter: List[int] = []

    def set_entity_id(self, entity_id: str):
        self.entity_id = entity_id

    async def wait_for_unlock(self):
        if self._has_entity():
            while True:
                self.locked_entities_counter[self.entity_id] += 1
                print(f"Waiting for profile {self.entity_id} to finish. Repeat {self.max_repeats}")
                await asyncio.sleep(self.wait)
                if self.locked_entities_counter[self.entity_id] >= self.max_repeats:
                    self.locked_entities_counter[self.entity_id] = 0
                    self.unlock_entity(self.entity_id)
                    break
    # async def __aenter__(self):
    #     while True:
    #         if self.is_profile_processed():
    #             print(f"Waiting for profile {self.profile} to finish. Repeat {self.max_repeats}")
    #             await asyncio.sleep(self.wait)
    #             self.max_repeats -= 1
    #         else:
    #             self._set_profile_process_id()
    #             return self
    #
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    #     await storage.driver.profile.refresh()
    #     self._delete_profile_process_id()

    def _has_entity(self):
        return self.entity_id is not None

    def _is_profile_processed(self):
        if self._has_entity():
            print('is', self.entity_id)
            return self.redis.client.hexists(self.hash, self.entity_id)
        return False

    def is_locked(self):
        return self._is_profile_processed() and self.max_repeats > 0

    def unlock_entities(self):
        for entity_id in list(self.locked_entities):
            self.unlock_entity(entity_id)

    def lock_entity(self):
        if self._has_entity():
            print('lock', self.entity_id)
            result = self.redis.client.hset(self.hash, self.entity_id, '1')
            if result:
                self.locked_entities.append(self.entity_id)

    def unlock_entity(self, entity_id):
        self.redis.client.hdel(self.hash, entity_id)
        if entity_id in self.locked_entities:
            self.locked_entities.remove(entity_id)
