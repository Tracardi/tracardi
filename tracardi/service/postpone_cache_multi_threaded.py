import logging

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

    def get(self, profile_id, default_value) -> bool:

        value_exists = self.exists(profile_id)

        logger.info(f"{self.hash}.{profile_id} exists {value_exists}")

        if not value_exists:
            default_value = 'yes' if default_value is True else "no"
            logger.info(f"Create {self.hash}.{profile_id} = {default_value}")
            self.redis.client.hset(self.hash, profile_id, default_value)
            return default_value == "yes"

        value_bson = self.redis.client.hget(self.hash, profile_id)
        value = value_bson.decode('utf-8')
        logger.info(f"Got {value} from {self.hash}.{profile_id}")

        return value == 'yes'

    def set(self, profile_id, value):
        value = "yes" if value else "no"
        logger.info(f"Set {self.hash}.{profile_id} = {value}")
        self.redis.client.hset(self.hash, profile_id, value)

    def reset(self, profile_id):
        logger.debug(f"Clean {self.hash}.{profile_id}")
        self.redis.client.hdel(self.hash, profile_id)
