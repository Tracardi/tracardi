from time import sleep

from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.exceptions.exception import ExpiredException


def test_memory_cache_add():
    mc = MemoryCache()
    try:
        mc['test'] = 1
        assert False
    except ValueError:
        assert True

    mc['test'] = CacheItem(data={"a": 1}, ttl=10)
    assert mc['test'].data == {"a": 1}


def test_memory_cache_ttl():
    mc = MemoryCache()

    mc['test'] = CacheItem(data={"a": 1}, ttl=2)
    assert 'test' in mc

    sleep(1)
    assert 'test' in mc
    assert mc['test'].data == {"a": 1}

    sleep(2)

    try:
        x = mc['test']
        assert False
    except ExpiredException:
        assert True

    assert 'test' not in mc


def test_memory_cache_usage_scenario():
    mc = MemoryCache()
    if 'x' not in mc:
        mc['x'] = CacheItem(data=1, ttl=2)
    assert mc['x'].data == 1

    sleep(1)

    # must be in cache
    if 'x' not in mc:
        assert False

    assert mc['x'].data == 1

    sleep(2)

    # must not be in cache
    if 'x' in mc:
        assert False

