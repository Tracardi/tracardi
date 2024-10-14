from collections import defaultdict

import json

from typing import Optional, List, Dict

from .entity import Entity, FlatEntity




class FlatEvent(FlatEntity):

    @staticmethod
    def as_entity(flat_event: 'FlatEvent'):
        if not flat_event:
            return None
        return Entity(id=flat_event['id'])

    @property
    def type(self) -> Optional[str]:
        return self.get('type', None)

    @property
    def properties(self) -> dict:
        return self.get('properties', {})

    @property
    def context(self) -> Optional[str]:
        return self.get('context', {})

    def is_async(self) -> bool:
        return 'config' in self and self['config'].get('async', True)

    def is_valid(self) -> bool:
        return self.get('metadata.valid', True)

    def has(self, value, equal=None) -> bool:
        if equal is None:
            return value in self
        return value in self and self[value] == equal

    def has_not_empty(self, value) -> bool:
        return value in self and self[value] is not None

    def set_if_not_instance(self, field: str, value, instance: type):
        if field not in self or not isinstance(self[field], instance):
            self[field] = value


class FlatEvents(list):
    def group_by_type(self):
        _indexed_flat_events: Dict[str, List[FlatEvent]] = defaultdict(list)
        for flat_event in self:
            _indexed_flat_events[flat_event.type].append(flat_event)
        return _indexed_flat_events


class EventDict(dict):
    pass

    @property
    def id(self) -> Optional[str]:
        return self.get('id', None)
