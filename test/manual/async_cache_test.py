import asyncio

from tracardi.service.decorators.async_cache import AsyncCache

async def main():
    @AsyncCache(ttl=1, throttle=3, use_context=False)
    async def my_async_function(param):
        print('call')
        # Perform some asynchronous operation and return a result
        return param

    # First 3 calls will execute the function and cache the results
    result1 = await my_async_function(1)
    print(result1)
    result2 = await my_async_function(1)
    print(result2)
    result3 = await my_async_function(1)
    print(result3)

    # Fourth call will return the cached result
    result4 = await my_async_function(1)
    print(result4)

    # Wait for more than a second, then the cache will be cleared
    await asyncio.sleep(0.8)

    # First 3 calls after the cache is cleared will execute the function and cache the results
    result5 = await my_async_function(1)
    print(result5)
    result6 = await my_async_function(1)
    print(result6)
    result7 = await my_async_function(1)
    print(result7)
    await asyncio.sleep(0.8)

    # Fourth call after the cache is cleared will return the cached result
    result8 = await my_async_function(1)
    print(result8)

asyncio.run(main())