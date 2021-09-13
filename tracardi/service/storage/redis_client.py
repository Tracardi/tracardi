import json
import redis
from tracardi.domain.profile import Profile
from tracardi.service.singleton import Singleton


class RedisClient(metaclass=Singleton):
    def __init__(self, host, port, db, password):
        self.connection = redis.Redis(host, port, db, password)

    def profile_exists(self, id):
        return self.connection.hexists("profile", id)

    def get_profile(self, id) -> Profile:
        profile_bson = self.connection.hget("profile", id)
        return Profile(**json.loads(profile_bson.decode('utf-8')))

    def save_profile(self, profile: Profile):
        return self.connection.hset("profile", profile.id, profile.json())
