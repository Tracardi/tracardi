from collections import defaultdict
from typing import List, Set, Optional, Union

from tracardi.config import tracardi
from tracardi.domain.entity import Entity, FlatEntity
from tracardi.domain.flat_session import FlatSession
from tracardi.domain.profile import Profile
from tracardi.service.adapter.cache_adaper_selector import mcache_adapter
from tracardi.common.singleton import Singleton
from tracardi.service.storage.redis.collections import Collection

batch = 3
i = 0
field_mappings = defaultdict(set)
redis_collections = {
    "profile": Collection.profile_fields,
    "event": Collection.event_fields,
    "session": Collection.session_fields,
}
_mcache = mcache_adapter()


class FieldMapper(metaclass=Singleton):
    """
    Saves added fields for session, profile, event.
    """

    def __init__(self):
        self.i = 0
        self.batch = 5

    def get_field_mapping(self, type: str) -> Set[str]:
        if type in redis_collections:
            return {item.decode() for item in _mcache.smembers(redis_collections[type])}
        return set()

    def add_field_mappings(self, type, entities: List[Union[Entity, FlatEntity]]) -> bool:
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
                _mcache.sadd(redis_collections[type], *list(field_maps))


def add_new_field_mappings(profile: Optional[Profile], flat_session: Optional[FlatSession]):
    # Add mappings
    if tracardi.expose_gui_api is True:
        if profile:
            FieldMapper().add_field_mappings('profile', [profile])

        if flat_session:
            FieldMapper().add_field_mappings('session', [flat_session])
