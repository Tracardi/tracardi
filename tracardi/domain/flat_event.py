from collections import defaultdict

import json

from datetime import datetime
from typing import Optional, List, Dict

from .entity import Entity, FlatEntity


class DottyEncoder(json.JSONEncoder):
    """Helper class for encoding of nested Dotty dicts into standard dict
    """

    def default(self, obj):
        """Return dict data of Dotty when possible or encode with standard format

        :param object: Input object
        :return: Serializable data
        """
        try:
            if hasattr(obj, '_data'):
                return obj._data
            elif isinstance(obj, datetime):
                # Convert datetime to an ISO formatted string
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return json.JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)


class Flat:

    def __init__(self, data):
        self._data = data

    def to_dict(self):
        """Return wrapped dictionary.
        This method does not copy wrapped dictionary.
        :return dict: Wrapped dictionary
        """
        return json.loads(self.to_json())

    def to_json(self):
        """Return wrapped dictionary as json string.
        This method does not copy wrapped dictionary.
        :return str: Wrapped dictionary as json string
        """
        return json.dumps(self._data, cls=DottyEncoder)


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

    def to_json(self):
        """
        Custom data serialisation
        """
        return json.dumps(self._data, cls=DottyEncoder)


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
