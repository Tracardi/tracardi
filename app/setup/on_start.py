import asyncio
import hashlib
import os

from app.domain.flow_action_plugin import FlowActionPlugin
from app.domain.record.flow_action_plugin_record import FlowActionPluginRecord
from app.process_engine.module_loader import load_callable

__local_dir = os.path.dirname(__file__)


async def add_plugin(module):
    plugin = load_callable(module, 'register')
    plugin_data = plugin()

    # Action plugin id is a hash of its module and className

    action_id = plugin_data.spec.module + plugin_data.spec.className
    action_id = hashlib.md5(action_id.encode()).hexdigest()

    action_plugin = FlowActionPlugin(id=action_id, plugin=plugin_data)
    record = FlowActionPluginRecord.encode(action_plugin)
    return await record.storage().save()


async def add_plugins():
    plugins = [
        'app.process_engine.action.v1.debug_payload_action',
        'app.process_engine.action.v1.start_action',
        'app.process_engine.action.v1.end_action',
        'app.process_engine.action.v1.if_action',
        'app.process_engine.action.v1.update_profile_action',
        'app.process_engine.action.v1.increase_views_action',
        'app.process_engine.action.v1.increase_visits_action',
        'app.process_engine.action.v1.read_session_action',
        'app.process_engine.action.v1.read_profile_action',
        'app.process_engine.action.v1.read_event_action',

        'app.process_engine.action.v1.properties.copy_property_action',
        'app.process_engine.action.v1.properties.cut_out_property_action',
        'app.process_engine.action.v1.properties.delete_property_action',

        # 'app.process_engine.action.new_event_action',
        # 'app.process_engine.action.remote_call_action',
    ]

    tasks = []
    for plugin in plugins:
        tasks.append(asyncio.create_task(add_plugin(plugin)))

    await asyncio.gather(*tasks)

