from typing import Callable, Optional, List

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.schema.table import Base


class SelectResult:

    def __init__(self, rows):
        self.rows = rows

    def map_to_objects(self, mapper: Callable):
        for row in self.rows:
            yield mapper(row)

    def map_to_object(self, mapper) -> Optional[Entity]:
        if self.rows:
            return mapper(self.rows)
        return None

    def as_named_entities(self, rewriter=None) -> List[NamedEntity]:
        if rewriter is None:
            return [NamedEntity(id=record.id, name=record.name) for record in self.rows]
        return [NamedEntity(id=record.id, name=rewriter(record)) for record in self.rows]

    def exists(self) -> bool:
        if self.rows is None:
            return False
        if isinstance(self.rows, Base):
            return True

        return bool(self.rows)


    def count(self):
        if self.exists():
            return len(self.rows)
        return 0