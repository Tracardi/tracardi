from tracardi.service.tracking.cache.prefix import get_cache_prefix


def test_get_cache_prefix():
    assert get_cache_prefix('88') == '88'
    assert get_cache_prefix('0a') == '0a'
    assert get_cache_prefix('aa') == 'aa'
    assert get_cache_prefix('@8') == '00'
