from app.domain.named_entity import NamedEntity
from app.service.storage.crud import StorageCrud


class Segment(NamedEntity):
    enabled: bool = True

    # Persistence

    def storage(self) -> StorageCrud:
        return StorageCrud("credential", Segment, entity=self)
