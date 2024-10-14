import zoneinfo

from datetime import datetime
from dotty_dict import Dotty

from tracardi.service.serializers import PickleSerializer


def test_serialize_deserialize():
    data = [Dotty({'date': datetime(2024, 10, 10, 6, 7, 46, 452145, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             'message': 'Filling cache -6941282368296714903:tracardi.service.cache.event_source:load_event_source_via_cache():source_id=5b564e75-3bd6-4da2-897a-d6de654881c1: ttl: 03:00.000s: [0.000]',
             'logger': 'tracardi.service.decorators.function_memory_cache', 'file': 'function_memory_cache.py',
             'line': 106, 'level': 'WARNING', 'stack_info': None, 'module': 'function_memory_cache',
             'class_name': '_async_exec', 'origin': 'root', 'event_id': None, 'profile_id': None, 'flow_id': None,
             'node_id': None, 'user_id': None}),
            Dotty({'date': datetime(2024, 10, 10, 6, 7, 46, 462157, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             'message': "Filling cache -6941282368296714903:tracardi.service.cache.event_validation:load_event_validation('custom',): ttl: 03:00.000s: [0.008]",
             'logger': 'tracardi.service.decorators.function_memory_cache', 'file': 'function_memory_cache.py',
             'line': 106, 'level': 'WARNING', 'stack_info': None, 'module': 'function_memory_cache',
             'class_name': '_async_exec', 'origin': 'root', 'event_id': None, 'profile_id': None, 'flow_id': None,
             'node_id': None, 'user_id': None})]

    ser = PickleSerializer.serialize(data)
    assert PickleSerializer.deserialize(ser) == data
