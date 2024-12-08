from tracardi.config import tracardi
from tracardi.service.adapter.cache.cache_protocol import CacheProtocol
from tracardi.service.adapter.cache.hcache_protocol import HCacheProtocol
from tracardi.service.adapter.cache.member_cache_protocol import MemberCacheProtocol
from tracardi.service.adapter.cache.pubsub_protocol import PubSubProtocol
from tracardi.service.decorators.run_once import run_once

_cache_adapter_var = tracardi.cache_adapter

if _cache_adapter_var == 'redis':
    from tracardi.service.adapter.cache.redis.redis_cache_adapter import RedisCacheAdapter
    from tracardi.service.adapter.cache.redis.redis_hcache_adapter import RedisHCacheAdapter
    from tracardi.service.adapter.cache.redis.redis_members_adapter import RedisMembersCacheAdapter
    from tracardi.service.adapter.cache.redis.redis_pubsub_adapter import RedisPubSubAdapter
elif _cache_adapter_var == 'upstash':
    from tracardi.service.adapter.cache.upstash.upstash_redis_cache_adapter import UpStashRedisCacheAdapter
    from tracardi.service.adapter.cache.upstash.upstash_redis_hcache_adapter import UpStashRedisHCacheAdapter
    from tracardi.service.adapter.cache.upstash.upstash_redis_members_adapter import UpStashRedisMembersCacheAdapter
    from tracardi.service.adapter.cache.upstash.upstash_redis_pubsub_adapter import UpStashRedisPubSubAdapter


@run_once
def cache_adapter() -> CacheProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _rcache_adapter = RedisCacheAdapter()
    elif _cache_adapter_var.lower() == 'upstash':
        _rcache_adapter = UpStashRedisCacheAdapter()
    else:
        raise ValueError(f"Unknown cache adapter `{_cache_adapter_var}`")

    return _rcache_adapter


@run_once
def hcache_adapter() -> HCacheProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _hcache_adapter = RedisHCacheAdapter()
    elif _cache_adapter_var.lower() == 'upstash':
        _hcache_adapter = UpStashRedisHCacheAdapter()
    else:
        raise ValueError(f"Unknown hcache adapter `{_cache_adapter_var}`")

    return _hcache_adapter


@run_once
def mcache_adapter() -> MemberCacheProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _mcache_adapter = RedisMembersCacheAdapter()
    elif _cache_adapter_var.lower() == 'upstash':
        _mcache_adapter = UpStashRedisMembersCacheAdapter()
    else:
        raise ValueError(f"Unknown mcache adapter `{_cache_adapter_var}`")

    return _mcache_adapter


@run_once
def pubsub_adapter() -> PubSubProtocol:
    if _cache_adapter_var.lower() == 'redis':
        _ps_cache_adapter = RedisPubSubAdapter()
    elif _cache_adapter_var.lower() == 'upstash':
        _ps_cache_adapter = UpStashRedisPubSubAdapter()
    else:
        raise ValueError(f"Unknown pubsub adapter `{_cache_adapter_var}`")

    return _ps_cache_adapter
