from tracardi.domain.record.flow_action_plugin_record import FlowActionPluginRecord

from tracardi.domain.flow_action_plugin import FlowActionPlugin
from tracardi.service.storage.factory import StorageFor


async def save_plugin(action_id, plugin_data):
    action_plugin = FlowActionPlugin(id=action_id, plugin=plugin_data)
    record = FlowActionPluginRecord.encode(action_plugin)
    return await StorageFor(record).index().save()
