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
            self.redis.client.hset(self.hash, profile_id, '1')
            return False

        return True

    def set(self, profile_id):
        self.redis.client.hset(self.hash, profile_id, '1')

    def reset(self, profile_id):
        self.redis.client.hdel(self.hash, profile_id)


class InstanceCache:

    def __init__(self, cache_type):
        logger.info(f"Cache for {cache_type} created")
        self.redis = RedisClient(redis_config.redis_host)
        self.hash = cache_type

    def exists(self, profile_id):
        return self.redis.client.hexists(self.hash, profile_id)

    def get_instance(self, profile_id, instance_id) -> Optional[str]:

        if not self.exists(profile_id):
            logger.info(f"Create instance {profile_id} = {instance_id}")
            self.redis.client.hset(self.hash, profile_id, instance_id)
            return None

        value_bson = self.redis.client.hget(self.hash, profile_id)
        value = value_bson.decode('utf-8')
        logger.info(f"Got instance {value} from {profile_id}")

        return value

    def set_instance(self, profile_id, instance_id):
        logger.info(f"Set instance {instance_id} for profile {profile_id}")
        self.redis.client.hset(self.hash, profile_id, instance_id)

    def reset(self, profile_id):
        logger.debug(f"Clean instance {profile_id}")
        self.redis.client.hdel(self.hash, profile_id)
