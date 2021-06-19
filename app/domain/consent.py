from typing import Optional

from app.domain.entity import Entity
from app.domain.third_party_processor import ThirdPartyProcessor
from app.domain.time_range_query import DatetimePayload
from app.service.storage.crud import StorageCrud


class Consent(Entity):
    description: Optional[str] = None
    third_party_processor: Optional[ThirdPartyProcessor] = None
    revoke: Optional[DatetimePayload] = None

    def storage(self) -> StorageCrud:
        return StorageCrud("consent", Consent, entity=self)
