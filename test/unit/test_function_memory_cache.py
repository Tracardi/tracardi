import asyncio

from tracardi.service.decorators.function_memory_cache import cache_for, cache, async_cache_for
import time


@cache_for(0.5, max_size=2, allow_null_values=False)
def x(a):
    return a


@async_cache_for(0.5, max_size=2, allow_null_values=False)
async def y(a):
    return a


def test_positive_path():
    assert x(1) == 1
    assert x(2) == 2

    assert 'unit.test_function_memory_cache:x' in cache

    assert cache['unit.test_function_memory_cache:x'].name == 'unit.test_function_memory_cache:x'
    assert len(cache['unit.test_function_memory_cache:x'].memory_buffer) == 2

    assert x(3) == 3
    assert x(4) == 4

    time.sleep(1)

    assert x(5) == 5

    assert len(cache['unit.test_function_memory_cache:x'].memory_buffer) == 1


def test_async_positive_path():
    async def main():

        assert await y(1) == 1
        assert await y(2) == 2

        assert 'unit.test_function_memory_cache:y' in cache
        assert cache['unit.test_function_memory_cache:y'].name == 'unit.test_function_memory_cache:y'
        assert len(cache['unit.test_function_memory_cache:y'].memory_buffer) == 2

        assert await y(3) == 3
        assert await y(4) == 4

        await asyncio.sleep(1)

        assert await y(5) == 5

        assert len(cache['unit.test_function_memory_cache:y'].memory_buffer) == 1

    asyncio.run(main())
