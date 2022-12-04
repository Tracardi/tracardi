import asyncio

from tracardi.service.synchronizer import ProfileTracksSynchronizer


def test_should_wait_for_unlock():

    async def main():
        es = ProfileTracksSynchronizer(ttl=3)
        es.lock_entity("1")
        assert es.is_locked("1")
        assert not es.is_locked("2")
        await es.wait_for_unlock("1")

    asyncio.run(main())
