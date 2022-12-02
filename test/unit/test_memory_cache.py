from time import sleep

import pytest

from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.exceptions.exception import ExpiredException


def test_should_delete_memory_cache():
    cache = MemoryCache("test")

    cache['test'] = CacheItem(data='xxx', ttl=0.5)

    del cache['test']

    assert 'test' not in cache


def test_should_not_allow_plain_values():
    cache = MemoryCache("test")
    with pytest.raises(ValueError):
        cache['test'] = 'xxx'


def test_should_expire_on_data_fetch():
    cache = MemoryCache("test")
    cache['test'] = CacheItem(data='xxx', ttl=0.5)
    assert cache['test'].data == 'xxx'
    sleep(1)
    with pytest.raises(ExpiredException):
        assert cache['test'].data


def test_should_expire_on_data_check():
    cache = MemoryCache("test")
    cache['test'] = CacheItem(data='xxx', ttl=0.5)
    assert cache['test'].data == 'xxx'
    sleep(1)
    assert 'test' not in cache


def test_should_be_purged():
    cache = MemoryCache("test", max_pool=2)
    cache['test1'] = CacheItem(data='xxx', ttl=0.5)
    cache['test2'] = CacheItem(data='yyy', ttl=3)
    cache['test3'] = CacheItem(data='zzz', ttl=0.5)

    # after 1 sec
    sleep(1)
    cache['test4'] = CacheItem(data='qqq', ttl=0.5)

    assert 'test2' in cache  # expires in 3 sec - left 2
    assert 'test4' in cache  # just added
    assert 'test1' not in cache
    assert 'test3' not in cache

    # after 2 sec
    sleep(1)
    assert 'test2' in cache  # 1 more sec left
    assert 'test4' not in cache  # expired - only 0.5 sec ttl
    assert 'test1' not in cache
    assert 'test3' not in cache

    sleep(1)

    # after 2 sec all expired

    assert 'test2' not in cache
    assert 'test4' not in cache
    assert 'test1' not in cache
    assert 'test3' not in cache

    # the cache is purged

    assert not cache.memory_buffer

    print(cache.memory_buffer)
