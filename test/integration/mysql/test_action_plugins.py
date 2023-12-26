from uuid import uuid4

import asyncio
import pytest

from tracardi.context import ServerContext, Context
from tracardi.domain.flow_action_plugin import FlowActionPlugin
from tracardi.service.plugin.domain.register import Spec, Plugin, MetaData
from tracardi.service.storage.mysql.service.action_plugin_service import ActionPluginService

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_load_all_plugins(event_loop):

    asyncio.set_event_loop(event_loop)

    with ServerContext(Context(production=True)):
        service = ActionPluginService()
        plugin_id = str(uuid4())
        try:
            # Insert a test plugin
            await service.insert(FlowActionPlugin(
                id=plugin_id,
                plugin=Plugin(
                    spec=Spec(className='Test', module='test'),
                    metadata=MetaData(name="test")
                )
            ))
            # Load all plugins
            plugins = await service.load_all()
            assert any(p.id == plugin_id for p in plugins.rows)

            plugin = await service.load_by_id(plugin_id)
            assert plugin.rows.id == plugin_id

            await service.update_by_id({"plugin_metadata_name": "new_value"}, plugin_id)
            updated_plugin = await service.load_by_id(plugin_id)
            assert updated_plugin.rows.plugin_metadata_name == 'new_value'

            filtered_plugins = await service.filter('collection')
            assert any(plugin.id == plugin_id for plugin in filtered_plugins.rows)

            await service.delete_by_id(plugin_id)
            deleted_plugin = await service.load_by_id(plugin_id)
            assert deleted_plugin.rows is None

        finally:
            # Cleanup
            await service.delete_by_id(plugin_id)




