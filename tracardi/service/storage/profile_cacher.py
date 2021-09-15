import json

from tracardi.config import redis_config

from tracardi.domain.profile import Profile
from tracardi.service.singleton import Singleton
from tracardi.service.storage.redis_client import RedisClient


class ProfileCache(metaclass=Singleton):

    def __init__(self):
        self.redis = RedisClient(redis_config.redis_host)
        self.hash = "profile-cache"

    def exists(self, id):
        return self.redis.client.hexists(self.hash, id)

    def get_profile(self, id) -> Profile:
        profile_bson = self.redis.client.hget(self.hash, id)
        return Profile(**json.loads(profile_bson.decode('utf-8')))

    def save_profile(self, profile: Profile):
        return self.redis.client.hset(self.hash, profile.id, profile.json())
