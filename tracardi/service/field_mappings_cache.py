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
}


class FieldMapper(metaclass=Singleton):

    def __init__(self):
        self.i = 0
        self.batch = 3
        self.redis = RedisClient()

    def get_field_mapping(self, type) -> Set[str]:
        return {item.decode() for item in self.redis.client.smembers(redis_collections[type])}

    def add_field_mappings(self, type, entities: List[Entity]):
        self.i += 1
        for entity in entities:
            field_mappings[type].update(entity.get_dotted_properties())

        if self.i > self.batch:
            self.save_cache()

    def save_cache(self):
        self.i = 0
        for type, field_maps in field_mappings.items():
            if len(field_maps) > 0:
                self.redis.client.sadd(redis_collections[type], *list(field_maps))

        field_mappings['profile'] = set()
        field_mappings['event'] = set()
