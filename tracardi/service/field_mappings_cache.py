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

    def __init__(self):
        self.i = 0
        self.batch = 3
        self.redis = RedisClient()

    def get_field_mapping(self, type) -> Set[str]:
        if type in redis_collections:
            return {item.decode() for item in self.redis.client.smembers(redis_collections[type])}
        return set()

    def add_field_mappings(self, type, entities: List[Entity]):
        self.i += 1

        new_props = set()
        for entity in entities:
            new_props.update(entity.get_dotted_properties())

        diff = new_props.difference(field_mappings[type])

        if not bool(diff):
            # No changes
            return

        # Update in memory cache
        field_mappings[type].update(new_props)

        if self.i > self.batch:
            self.save_cache()

    def save_cache(self):
        self.i = 0
        for type, field_maps in field_mappings.items():
            if len(field_maps) > 0 and type in redis_collections:
                self.redis.client.sadd(redis_collections[type], *list(field_maps))
