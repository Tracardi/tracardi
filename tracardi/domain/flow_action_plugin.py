from typing import Optional, Any
from tracardi.service.plugin.domain.register import Plugin
from .entity import Entity
from .metadata import Metadata
from .settings import Settings
from .time import Time
from .value_object.storage_info import StorageInfo
from ..service.utils.date import now_in_utc


class FlowActionPlugin(Entity):

    """
    This object can not be loaded without encoding.
    Load it as FlowActionPluginRecord and then decode.
    """

    metadata: Optional[Metadata] = None
    plugin: Plugin
    settings: Optional[Settings] = Settings()

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=now_in_utc()
            ))
        super().__init__(**data)

    # Persistence

    """
    Do not use load method. This object must be decoded from FlowActionPluginRecord
    """

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'action',
            FlowActionPlugin
        )
