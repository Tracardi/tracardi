from tracardi.service.utils.date import now_in_utc

from datetime import datetime
from typing import Optional, Any, Callable
from ..entity import Entity
from ..flow_action_plugin import FlowActionPlugin
from ..metadata import Metadata
from ..settings import Settings
from ..time import Time
from ..value_object.storage_info import StorageInfo
from ...service.module_loader import import_package, load_callable
from tracardi.domain.flow import PluginRecord


class FlowActionPluginRecord(Entity):
    metadata: Optional[Metadata] = None
    plugin: PluginRecord
    settings: Optional[Settings] = Settings()

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(time=Time())
        super().__init__(**data)

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
        return FlowActionPlugin.model_construct(_fields_set=self.model_fields_set, **data)

    def get_validator(self) -> Callable:
        module = import_package(self.plugin.spec.module)
        return load_callable(module, 'validate')
