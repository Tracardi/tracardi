# import asyncio
# import logging
# from typing import Union
# from tracardi.config import tracardi
# from tracardi.exceptions.log_handler import log_handler
# from tracardi.service.storage.redis_client import RedisClient
#
# logger = logging.getLogger(__name__)
# logger.setLevel(tracardi.logging_level)
# logger.addHandler(log_handler)
#
#
# class ProfileTracksSynchronizer:
#     def __init__(self, wait=0.1, ttl=5):
#         self.wait = wait
#         self.ttl = ttl
#         self.redis = RedisClient()
#         self.hash = "synchronizer"
#
#     def _get_key(self, key: str) -> str:
#         return f"{self.hash}:{key}"
#
#     async def wait_for_unlock(self, key: str, seq: Union[str, int] = None):
#         while True:
#             if self.is_locked(key):
#                 logger.info(
#                     f"Tracker payload - {seq}: Waiting {self.wait}s for profile {key} to finish. Expires in {self.expires_in(key)}s")
#                 await asyncio.sleep(self.wait)
#                 continue
#             self.unlock_entity(key)
#             break
#
#     def expires_in(self, key: str):
#         return self.redis.ttl(self._get_key(key))
#
#     def is_locked(self, key: str):
#         return self.redis.exists(self._get_key(key))
#
#     def unlock_entities(self, keys: str):
#         for key in keys:
#             self.unlock_entity(key)
#
#     def lock_entity(self, key: str):
#         key = self._get_key(key)
#         result = self.redis.set(key, '1', ex=self.ttl)
#         if result is True:
#             logger.debug(f"Locking key {key} {result}")
#
#     def unlock_entity(self, key: str):
#         key = self._get_key(key)
#         result = self.redis.delete(key)
#         logger.debug(f"UnLocking key {key} {result}")
#
#
# profile_synchronizer = ProfileTracksSynchronizer(
#     wait=tracardi.sync_profile_tracks_wait,
#     ttl=5
# )
