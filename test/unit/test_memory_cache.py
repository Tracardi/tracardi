from time import sleep

import pytest

from tracardi.context import ServerContext, Context
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.exceptions.exception import ExpiredException


def test_should_delete_memory_cache():
    with ServerContext(Context(production=False)):
        cache = MemoryCache("name")

        cache['key'] = CacheItem(data='value', ttl=0.5)

        assert 'key' in cache

        del cache['key']

        assert 'key' not in cache


def test_should_not_allow_plain_values():
    with ServerContext(Context(production=False)):
        cache = MemoryCache("name")
        with pytest.raises(ValueError):
            cache['key'] = 'value'


def test_should_expire_on_data_fetch():
    with ServerContext(Context(production=False)):
        cache = MemoryCache("name")
        cache['key'] = CacheItem(data='value', ttl=0.5)
        assert cache['key'].data == 'value'
        sleep(1)
        with pytest.raises(ExpiredException):
            assert cache['key'].data


def test_should_expire_on_data_check():
    with ServerContext(Context(production=False)):
        cache = MemoryCache("test")
        cache['test'] = CacheItem(data='xxx', ttl=0.5)
        assert cache['test'].data == 'xxx'
        sleep(1)
        assert 'test' not in cache


def test_should_be_purged():
    with ServerContext(Context(production=False)):
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

def test_is_expired_check():
    with ServerContext(Context(production=False)):
        cache = MemoryCache("test")
        cache['test'] = CacheItem(data='xxx', ttl=0.5)
        assert not cache.is_expired('test')
        sleep(1)
        assert cache.is_expired('test')


def test_context_must_work_per_context():
    with ServerContext(Context(production=False)):
        cache = MemoryCache("test")
        with ServerContext(Context(production=True)):
            cache['test'] = CacheItem(data='xxx', ttl=5)
            assert 'test' in cache
        with ServerContext(Context(production=False)):
            assert 'test' not in cache

