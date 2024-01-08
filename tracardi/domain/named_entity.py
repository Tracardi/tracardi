from typing import Any

from tracardi.domain.entity import Entity


class NamedEntity(Entity):
    name: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.id = self.id.lower()

    def is_empty(self):
        return self.id == '' or self.id is None or self.name is None or self.id == ''
