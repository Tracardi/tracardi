from datetime import datetime
from typing import Optional, Any
from tracardi_plugin_sdk.domain.register import Plugin

from tracardi.service.storage.crud import StorageCrud
from .entity import Entity
from .metadata import Metadata
from .settings import Settings
from .time import Time


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

    def storage(self) -> StorageCrud:
        return StorageCrud("action", FlowActionPlugin, entity=self)
