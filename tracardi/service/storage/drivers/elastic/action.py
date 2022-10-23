from tracardi.domain.settings import Settings
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager, StorageForBulk
from tracardi.service.plugin.domain.register import Plugin

from tracardi.domain.record.flow_action_plugin_record import FlowActionPluginRecord

from tracardi.domain.flow_action_plugin import FlowActionPlugin
from tracardi.service.storage.factory import StorageFor


async def save_plugin(plugin_data: Plugin, settings=None):
    if settings is None:
        settings = Settings()

    action_plugin = FlowActionPlugin(id=plugin_data.spec.get_id(), plugin=plugin_data, settings=settings)
    record = FlowActionPluginRecord.encode(action_plugin)
    return await StorageFor(record).index().save()


async def load_by_id(id: str):
    return await storage_manager('action').load(id)


async def load_all(start: int = 0, limit: int = 100) -> StorageRecords:
    return await StorageForBulk().index('action').load(start, limit)


async def refresh():
    return await storage_manager('action').refresh()


async def flush():
    return await storage_manager('action').flush()


async def filter(purpose: str, limit: int = 500):
    query = {
        "size": limit,
        "query": {
            "term": {
                "plugin.metadata.purpose": purpose
            }
        }
    }
    return await storage_manager("action").query(query)
