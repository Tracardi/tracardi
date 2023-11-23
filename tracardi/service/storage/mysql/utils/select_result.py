from typing import Callable, Optional, List, Generator, Any

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.schema.table import Base


class SelectResult:

    def __init__(self, rows):
        self.rows = rows

    def map_to_objects(self, mapper: Callable) -> Generator[Any, Any, None]:
        if not isinstance(self.rows, list):
            yield mapper(self.rows)
        else:
            for row in self.rows:
                yield mapper(row)

    def map_to_object(self, mapper) -> Optional[Entity]:
        if self.rows:
            return mapper(self.rows)
        return None

    def map_first_to_object(self, mapper)  -> Optional[Entity]:
        if self.has_multiple_records():
            return mapper(self.rows[0])
        return self.map_to_object(mapper)

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

    def has_multiple_records(self) -> bool:
        return isinstance(self.rows, list)

    def count(self):
        if self.exists():
            if self.has_multiple_records():
                return len(self.rows)
            return 1
        return 0