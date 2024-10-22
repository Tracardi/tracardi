import asyncio

import pytest
from time import sleep

from tracardi.context import ServerContext, Context
from tracardi.service.decorators.function_memory_cache import cache_for, async_cache_for

run_counter = 0


@cache_for(0.5, max_size=2, allow_null_values=False)
def x(a):
    return a


@async_cache_for(.5, max_size=2, allow_null_values=False, lock=False)
async def y(a):
    global run_counter
    run_counter += 1
    await asyncio.sleep(.1)
    return a


@async_cache_for(3, max_size=10, allow_null_values=False, lock=True)
async def y_locked(a):
    global run_counter
    run_counter += 1
    await asyncio.sleep(.1)
    return a

counter = 0

@async_cache_for(.5, max_size=10, allow_null_values=False, lock=True, timeout=.1)
async def timeout(a):
    global counter
    if counter > 0:
        await asyncio.sleep(.2)
    else:
        await asyncio.sleep(.02)
    counter += 1
    return a

# def test_positive_path():
#     with ServerContext(Context(production=True)):
#         context = get_context()
#         context_hash = context.__hash__()
#         fnc_str = f"{context_hash}:unit.test_function_memory_cache:x"
#
#         assert x(1) == 1
#         assert x(2) == 2
#
#         assert fnc_str in cache
#
#         assert cache[fnc_str].name == fnc_str
#         assert len(cache[fnc_str].memory_buffer) == 2
#
#         assert x(3) == 3
#         assert x(4) == 4
#
#         sleep(1)
#
#         assert x(5) == 5
#
#         assert len(cache[fnc_str].memory_buffer) == 1
#
#
# def test_async_positive_path():
#     async def main():
#         with ServerContext(Context(production=True)):
#             context = get_context()
#             context_hash = context.__hash__()
#             fnc_str = f"{context_hash}:unit.test_function_memory_cache:y"
#
#             assert await y(1) == 1
#             assert await y(2) == 2
#
#             assert fnc_str in cache
#             assert cache[fnc_str].name == fnc_str
#             assert len(cache[fnc_str].memory_buffer) == 2
#
#             assert await y(3) == 3
#             assert await y(4) == 4
#
#             await asyncio.sleep(1)
#
#             assert await y(5) == 5
#
#             assert len(cache[fnc_str].memory_buffer) == 1
#
#     asyncio.run(main())
#
#
# def test_async_positive_path_blocking():
#     async def main():
#         global run_counter
#
#         with ServerContext(Context(production=True)):
#             run_counter = 0
#
#             result = await asyncio.gather(
#                 y_locked(1),
#                 y_locked(1)
#             )
#             assert result == [1, 1]
#             assert run_counter == 1
#
#     asyncio.run(main())
#
#
# def test_async_positive_path_no_blocking():
#     async def main():
#         global run_counter
#
#         with ServerContext(Context(production=True)):
#             run_counter = 0
#
#             result = await asyncio.gather(
#                 y(1),
#                 y(1)
#             )
#             assert result == [1, 1]
#             assert run_counter == 2
#
#     asyncio.run(main())
#
#
# def test_delete():
#     with ServerContext(Context(production=True)):
#         context = get_context()
#         context_hash = context.__hash__()
#         fnc_str = f"{context_hash}:unit.test_function_memory_cache:x"
#
#         assert x(1) == 1
#         assert fnc_str in cache
#         assert len(cache[fnc_str].memory_buffer) == 1
#
#         delete_cache(x, 1)
#
#         assert len(cache[fnc_str].memory_buffer) == 0
#
#
# def test_multi_tenant():
#     with ServerContext(Context(production=True)):
#         assert 1 == x(1)
#         assert has_cache(x, 1)
#         delete_cache(x, 1)
#         assert not has_cache(x, 1)
#
#     with ServerContext(Context(production=False)):
#         assert 1 == x(1)
#
#     with ServerContext(Context(production=True)):
#         assert not has_cache(x, 1)
#         with ServerContext(Context(production=False)):
#             assert has_cache(x, 1)
#
#
# def test_incorrect_caching():
#     with ServerContext(Context(production=True)):
#         with pytest.raises(TypeError):
#             @cache_for(0.5, max_size=2, allow_null_values=False)
#             async def incorrect_tagging_1(a):
#                 return a
#
#         with pytest.raises(TypeError):
#             @async_cache_for(0.5, max_size=2, allow_null_values=False)
#             def incorrect_tagging_2(a):
#                 return a


def test_async_positive_path_blocking_separation():
    async def main():
        global run_counter

        with ServerContext(Context(production=True)):
            run_counter = 0

            await y_locked(1)

            result = await asyncio.gather(
                y_locked(1),
                y_locked(2),
                y_locked(2),
                y_locked(1),
                y_locked(1),
                y_locked(1),
            )
            assert result == [1, 2, 2, 1, 1, 1]
            assert run_counter == 2

    asyncio.run(main())



def test_async_timeout():
    async def main():

        with ServerContext(Context(production=True)):
            with pytest.raises(asyncio.exceptions.TimeoutError):
                await timeout(1)


    asyncio.run(main())

def test_async_timeout_last_cache_value():
    async def main():

        with ServerContext(Context(production=True)):
            assert 1 == await timeout(1)  # No timeout
            sleep(.6)
            assert 1 == await timeout(1)  # This time timeouts but returns old value.
            assert 1 == await timeout(1)  # This time timeouts but returns old value.


    asyncio.run(main())