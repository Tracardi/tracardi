from typing import List

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    debug: bool = False
    events: List[NamedEntity] = []

    def get_allowed_event_types(self) -> List[str]:
        return [event.id for event in self.events]
