import asyncio

from tracardi.service.pool_manager import PoolManager

def test_should_group_pool_items():
    async def main():

        result = []

        async def purge(items):
            result.append(items)

        async with PoolManager(3, on_pool_purge=purge, replace_item_on_append=False) as m:
            await m.append(1)
            await m.append(2)
            await m.append(3)
            await m.append(4)
            await m.append(5)
            await m.append(5)

        await asyncio.sleep(1)

        return result

    result = asyncio.run(main())
    assert result == [[1, 2, 3], [4, 5, 5]]


def test_should_group_pool_items_and_time_out():
    async def main():

        result = []

        async def purge(items):
            result.append(items)

        async with PoolManager(3, on_pool_purge=purge, replace_item_on_append=False) as m:
            m.set_ttl(
                loop=asyncio.get_running_loop(),
                ttl=0.5
            )
            await m.append(1)
            await m.append(2)
            await asyncio.sleep(1)
            await m.append(3)
            await m.append(4)
            await m.append(5)
            await m.append(5)

        await asyncio.sleep(1)

        return result

    result = asyncio.run(main())
    assert result == [[1, 2], [3, 4, 5], [5]]


def test_should_run_without_context():
    async def main():
        result = []

        async def purge(items):
            result.append(items)

        pool = PoolManager(4, purge)
        pool.set_ttl(
            loop=asyncio.get_running_loop(),
            ttl=0.5
        )
        await pool.append(1)
        await pool.append(2)

        await pool.purge()
        await pool.append(3)
        await pool.append(4)
        await pool.append(5)
        await pool.append(6)
        await pool.append(7)

        await asyncio.sleep(1)
        await pool.append(9)
        await pool.append(10)
        await pool.purge()
        await pool.append(11)
        await pool.append(121)
        await pool.append(122)

        await asyncio.sleep(1)
        await pool.append(123)
        await pool.append(124)
        await pool.append(125)
        await pool.purge()

        return result
    result = asyncio.run(main())
    assert result == [[1, 2], [3, 4, 5, 6], [7], [9, 10], [11, 121, 122], [123, 124,125]]