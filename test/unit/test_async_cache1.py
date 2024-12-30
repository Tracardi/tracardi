import asyncio

import pytest
from time import sleep

from tracardi.context import ServerContext, Context
from tracardi.common.decorator.async_cache import AsyncCache

run_counter = 0


@AsyncCache(.5, allow_null_values=False, lock=False)
async def y(a):
    global run_counter
    run_counter += 1
    await asyncio.sleep(.1)
    return a


@AsyncCache(3, allow_null_values=False, lock=True)
async def y_locked(a):
    global run_counter
    run_counter += 1
    await asyncio.sleep(.1)
    return a


counter = 0


@AsyncCache(.3, allow_null_values=False, lock=True, timeout=.1)
async def timeout(a):
    global counter
    if counter > 0:
        await asyncio.sleep(.2)
    else:
        await asyncio.sleep(.02)
    counter += 1
    return a


@AsyncCache(0, allow_null_values=False, lock=False)
async def error(a):
    global counter
    if counter > 0:
        raise ValueError("test")
    counter += 1
    return a


@AsyncCache(0, allow_null_values=False, lock=False, return_cache_on_error=True)
async def error_with_cache(a):
    global counter
    if counter > 0:
        raise ValueError("test")
    counter += 1
    return a


@pytest.mark.asyncio
async def test_async_positive_path_blocking_separation():
    global run_counter

    with ServerContext(Context(production=True)):
        run_counter = 0

        # await y_locked(1)

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


@pytest.mark.asyncio
async def test_async_timeout():
    global counter
    counter = 1
    with ServerContext(Context(production=True)):
        with pytest.raises(asyncio.exceptions.TimeoutError):
            await timeout(1)


@pytest.mark.asyncio
async def test_async_timeout_last_cache_value():
    global counter
    counter = 0
    with ServerContext(Context(production=True)):
        assert 1 == await timeout(1)  # No timeout
        sleep(.35)
        assert 1 == await timeout(1)  # This time timeouts but returns old value.
        assert 1 == await timeout(1)  # This time timeouts but returns old value.


@pytest.mark.asyncio
async def test_no_cache_on_error():
    global counter
    counter = 0
    with ServerContext(Context(production=True)):
        assert 1 == await error(1)
        with pytest.raises(ValueError):
            await error(1)


@pytest.mark.asyncio
async def test_cache_on_error():
    global counter
    counter = 0
    with ServerContext(Context(production=True)):
        assert 1 == await error_with_cache(1)
        assert 1 == await error_with_cache(1)
