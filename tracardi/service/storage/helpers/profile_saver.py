from tracardi.config import redis_config
from tracardi.domain.profile import Profile
from tracardi.service.storage.factory import StorageFor
from tracardi.service.storage.redis_client import RedisClient


async def save_profile(profile: Profile):
    if redis_config.redis_host is not False:
        redis_client = RedisClient(redis_config.redis_host, redis_config.redis_port,
                                   redis_config.redis_db, redis_config.redis_password)
        redis_client.save_profile(profile)
    return await StorageFor(profile).index().save()
