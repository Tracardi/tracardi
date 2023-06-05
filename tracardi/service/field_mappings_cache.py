from collections import defaultdict
from typing import List, Set

from tracardi.domain.entity import Entity
from tracardi.service.singleton import Singleton
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient

batch = 3
i = 0
field_mappings = defaultdict(set)
redis_collections = {
    "profile": Collection.profile_fields,
    "event": Collection.event_fields,
    "session": Collection.session_fields,
}


class FieldMapper(metaclass=Singleton):

    """
    Saves added fields for session, profile, event.
    """

    def __init__(self):
        self.i = 0
        self.batch = 5
        self.redis = RedisClient()

    def get_field_mapping(self, type) -> Set[str]:
        if type in redis_collections:
            return {item.decode() for item in self.redis.smembers(redis_collections[type])}
        return set()

    def add_field_mappings(self, type, entities: List[Entity]) -> bool:
        new_props = set()
        for entity in entities:
            self.i += 1
            new_props.update(entity.get_dotted_properties())

        diff = new_props.difference(field_mappings[type])

        if not bool(diff):
            # No changes
            return False

        # Update in memory cache
        field_mappings[type].update(new_props)

        if self.i > self.batch:
            self.save_cache()

        return True

    def save_cache(self):
        self.i = 0
        for type, field_maps in field_mappings.items():
            if len(field_maps) > 0 and type in redis_collections:
                self.redis.sadd(redis_collections[type], *list(field_maps))
