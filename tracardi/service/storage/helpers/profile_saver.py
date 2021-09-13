from tracardi.config import redis_config, elastic
from tracardi.domain.profile import Profile
from tracardi.service.storage.factory import StorageFor, storage
from tracardi.service.storage.redis_client import RedisClient


async def save_profile(profile: Profile):
    if redis_config.redis_host is not False:
        redis_client = RedisClient(redis_config.redis_host, redis_config.redis_port,
                                   redis_config.redis_db, redis_config.redis_password)
        redis_client.save_profile(profile)
    result = await StorageFor(profile).index().save()
    if elastic.self.refresh_profiles_after_save:
        await storage('profile').flush()
    return result
