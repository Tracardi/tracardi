from typing import Optional

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.redis.driver.redis_client import RedisClient

logger = get_logger(__name__)


class PostponeCache:

    def __init__(self, cache_type):
        logger.info(f"Cache for {cache_type} created")
        self.redis = RedisClient()
        self.hash = cache_type

    def exists(self, profile_id):
        return self.redis.hexists(self.hash, profile_id)

    def get(self, profile_id) -> bool:

        if not self.exists(profile_id):
            self.redis.hset(self.hash, profile_id, '1')
            return False

        return True

    def set(self, profile_id):
        self.redis.hset(self.hash, profile_id, '1')

    def reset(self, profile_id):
        self.redis.hdel(self.hash, profile_id)


class InstanceCache:

    def __init__(self, cache_type):
        logger.info(f"Cache for {cache_type} created")
        self.redis = RedisClient()
        self.hash = cache_type

    def exists(self, profile_id):
        return self.redis.hexists(self.hash, profile_id)

    def get_instance(self, profile_id, instance_id) -> Optional[str]:

        if not self.exists(profile_id):
            logger.info(f"Create instance {instance_id} for profile {profile_id}")
            self.redis.hset(self.hash, profile_id, instance_id)
            return None

        value_bson = self.redis.hget(self.hash, profile_id)
        value = value_bson.decode('utf-8')

        return value

    def set_instance(self, profile_id, instance_id):
        logger.info(f"Destination sync for profile {profile_id} is going to be sent from worker instance {instance_id}")
        self.redis.hset(self.hash, profile_id, instance_id)

    def reset(self, profile_id):
        logger.debug(f"Clean profile worker instance {profile_id}")
        self.redis.hdel(self.hash, profile_id)
