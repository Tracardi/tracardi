import asyncio
import logging
from typing import Optional
from tracardi.domain.entity import Entity
from tracardi.config import redis_config, tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver import storage
from tracardi.service.storage.redis_client import AsyncRedisClient, RedisClient

logger = logging.getLogger('tracardi.api.event_server')
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


# todo try to use this.
class AsyncProfileTracksSynchronizer:
    def __init__(self, profile: Optional[Entity], wait=0.1):
        self.wait = wait
        self.profile = profile
        self.redis = AsyncRedisClient(redis_config.redis_host)
        self.hash = "profile-blocker"

    async def __aenter__(self):
        max_repeats = 10
        while True:
            if await self._is_profile_processed() and max_repeats > 0:
                logger.info(f"Waiting for /track/{self.profile.id} to finish. Repeat {max_repeats}")
                await asyncio.sleep(self.wait)
                max_repeats -= 1
            else:
                await self._set_profile_process_id()
                return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._delete_profile_process_id()

    def _has_profile(self):
        return self.profile is not None and self.profile.id is not None

    async def _is_profile_processed(self):
        if self._has_profile():
            return await self.redis.client.hexists(self.hash, self.profile.id)
        return False

    async def _delete_profile_process_id(self):
        if self._has_profile():
            return await self.redis.client.hdel(self.hash, self.profile.id)

    async def _set_profile_process_id(self):
        if self._has_profile():
            return await self.redis.client.hset(self.hash, self.profile.id, '1')


class ProfileTracksSynchronizer:
    def __init__(self, profile: Optional[Entity], wait=0.1, max_repeats=20):
        self.wait = wait
        self.profile = profile
        self.redis = RedisClient()
        self.hash = "profile-blocker"
        self.max_repeats = max_repeats

    async def __aenter__(self):
        while True:
            if self._is_profile_processed() and self.max_repeats > 0:
                logger.info(f"Waiting for /track/{self.profile.id} to finish. Left repeats {self.max_repeats}")
                await asyncio.sleep(self.wait)
                self.max_repeats -= 1
            else:
                self._set_profile_process_id()
                return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await storage.driver.profile.refresh()
        self._delete_profile_process_id()

    def _has_profile(self):
        return self.profile is not None and self.profile.id is not None

    def _is_profile_processed(self):
        if self._has_profile():
            return self.redis.client.hexists(self.hash, self.profile.id)
        return False

    def _delete_profile_process_id(self):
        if self._has_profile():
            return self.redis.client.hdel(self.hash, self.profile.id)

    def _set_profile_process_id(self):
        if self._has_profile():
            return self.redis.client.hset(self.hash, self.profile.id, '1')
