import asyncio
import pytest
from tracardi.common.decorator.async_cache import AsyncCache

@pytest.mark.asyncio
async def test_async_cache_basic():
    call_count = 0

    @AsyncCache(ttl=.1, max_one_cache_fill_every=0, use_context=False)
    async def my_async_function(param):
        nonlocal call_count
        call_count += 1
        print('call')
        return param

    # First 3 calls should execute the function and cache the results
    result1 = await my_async_function(1)
    assert result1 == 1
    assert call_count == 1

    result2 = await my_async_function(1)
    assert result2 == 1
    assert call_count == 1

    # Now it ttl exprires
    await asyncio.sleep(.15)

    result = await my_async_function(1)
    assert result == 1
    assert call_count == 2

    # Now works throttle
    result = await my_async_function(1)
    assert result == 1
    assert call_count == 2



@pytest.mark.asyncio
async def test_async_cache_throttle():
    call_count = 0

    @AsyncCache(ttl=0, max_one_cache_fill_every=0.1, use_context=False)
    async def my_async_function(param):
        nonlocal call_count
        call_count += 1
        print('call')
        return param

    # First 3 calls should execute the function and cache the results
    result1 = await my_async_function(1)
    assert result1 == 1
    assert call_count == 1

    result2 = await my_async_function(1)
    assert result2 == 1
    assert call_count == 1

    # Now it ttl expires
    await asyncio.sleep(.15)

    for _ in range(0, 10):
        result = await my_async_function(1)
        assert result == 1
        # assert call_count == 2
        await asyncio.sleep(.02)



@pytest.mark.asyncio
async def test_async_cache_ttl_throttle():
    call_count = 0

    @AsyncCache(ttl=0.1, max_one_cache_fill_every=0.3, use_context=False)
    async def my_async_function(param):
        nonlocal call_count
        call_count += 1
        print('call')
        return param

    # First 3 calls should execute the function and cache the results
    result1 = await my_async_function(1)
    assert result1 == 1
    assert call_count == 1

    result2 = await my_async_function(1)
    assert result2 == 1
    assert call_count == 1

    # Now it ttl expires
    await asyncio.sleep(.15)

    for _ in range(0, 40):
        result = await my_async_function(1)
        assert result == 1
        # assert call_count == 2
        await asyncio.sleep(.02)

