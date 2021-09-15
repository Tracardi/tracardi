from datetime import datetime
from typing import Optional, Any
from ..entity import Entity
from ..flow_action_plugin import FlowActionPlugin
from tracardi.domain.flow import PluginRecord
from ..metadata import Metadata
from ..settings import Settings
from ..time import Time
from ..value_object.storage_info import StorageInfo


class FlowActionPluginRecord(Entity):
    metadata: Optional[Metadata]
    plugin: PluginRecord
    settings: Optional[Settings] = Settings()

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    # Persistence
    #
    # def storage(self) -> StorageCrud:
    #     return StorageCrud("action", FlowActionPluginRecord, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'action',
            FlowActionPluginRecord
        )

    @staticmethod
    def encode(action: FlowActionPlugin) -> 'FlowActionPluginRecord':
        return FlowActionPluginRecord(
            id=action.id,
            plugin=PluginRecord.encode(action.plugin),
            metadata=action.metadata,
            settings=action.settings
        )

    def decode(self) -> FlowActionPlugin:
        data = {
            "id": self.id,
            "plugin": self.plugin.decode(),
            "metadata": self.metadata,
            "settings": self.settings
        }
        return FlowActionPlugin.construct(_fields_set=self.__fields_set__, **data)
