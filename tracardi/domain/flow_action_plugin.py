from datetime import datetime
from typing import Optional, Any, Callable
from tracardi.service.plugin.domain.register import Plugin
from .entity import Entity
from .metadata import Metadata
from .settings import Settings
from .time import Time
from tracardi.service.module_loader import import_package, load_callable
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


    def get_validator(self) -> Callable:
        module = import_package(self.plugin.spec.module)
        return load_callable(module, 'validate')
