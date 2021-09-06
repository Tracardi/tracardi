from datetime import datetime
from typing import Optional, Any
from tracardi_plugin_sdk.domain.register import Plugin
from .entity import Entity
from .metadata import Metadata
from .settings import Settings
from .time import Time
from .value_object.storage_info import StorageInfo


class FlowActionPlugin(Entity):
    metadata: Optional[Metadata]
    plugin: Plugin
    settings: Optional[Settings] = Settings()

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    # Persistence

    # def storage(self) -> StorageCrud:
    #     return StorageCrud("action", FlowActionPlugin, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'action',
            FlowActionPlugin
        )
