from tracardi.service.storage.factory import storage_manager
from tracardi_plugin_sdk.domain.register import Plugin

from tracardi.domain.record.flow_action_plugin_record import FlowActionPluginRecord

from tracardi.domain.flow_action_plugin import FlowActionPlugin
from tracardi.service.storage.factory import StorageFor


async def save_plugin(plugin_data: Plugin):
    action_plugin = FlowActionPlugin(id=plugin_data.spec.get_id(), plugin=plugin_data)
    record = FlowActionPluginRecord.encode(action_plugin)
    return await StorageFor(record).index().save()


async def load_by_id(id: str):
    return await storage_manager('action').load(id)


async def refresh():
    return await storage_manager('action').refresh()


async def flush():
    return await storage_manager('action').flush()
