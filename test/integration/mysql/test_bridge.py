import asyncio
import pytest
from uuid import uuid4

from tracardi.context import ServerContext, Context
from tracardi.domain.bridge import Bridge
from tracardi.service.storage.mysql.service.bridge_service import BridgeService

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
# Test for loading all bridges
async def test_bridges(event_loop):
    asyncio.set_event_loop(event_loop)

    with ServerContext(Context(production=False)):
        service = BridgeService()
        bridge_id = uuid4().hex
        try:

            await service.insert(Bridge(
                id=bridge_id,
                name='test',
                type='rest'
            ))

            bridges = await service.load_all()
            assert bridges.has_multiple_records()
            bridge = await service.load_by_id(bridge_id)
            assert bridge.rows.id == bridge_id
        finally:
            await service.delete_by_id(bridge_id)
            bridge = await service.load_by_id(bridge_id)
            assert bridge.exists() is False
