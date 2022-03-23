import logging
from typing import Optional

from tracardi.config import tracardi, redis_config
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.redis_client import RedisClient

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class PostponeCache:

    def __init__(self, cache_type):
        logger.info(f"Cache for {cache_type} created")
        self.redis = RedisClient(redis_config.redis_host)
        self.hash = cache_type

    def exists(self, profile_id):
        return self.redis.client.hexists(self.hash, profile_id)

    def get(self, profile_id) -> bool:

        if not self.exists(profile_id):
            logger.info(f"Create {self.hash}.{profile_id}")
            self.redis.client.hset(self.hash, profile_id, '1')
            return False

        logger.info(f"Exists {self.hash}.{profile_id}")

        return True

    def set(self, profile_id):
        logger.info(f"Set {self.hash}.{profile_id}")
        self.redis.client.hset(self.hash, profile_id, '1')

    def reset(self, profile_id):
        logger.debug(f"Clean {self.hash}.{profile_id}")
        self.redis.client.hdel(self.hash, profile_id)
