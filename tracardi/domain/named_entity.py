from tracardi.domain.entity import Entity


class NamedEntity(Entity):
    name: str

    def is_empty(self):
        return self.id == '' or self.id is None or self.name is None or self.id == ''
